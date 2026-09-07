"""Command-line entry point for deterministic scenario integration."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path
from time import perf_counter_ns
from typing import Any

from kyra.baseline import BaselineBuilder, save_baseline
from kyra.contracts import ChangeType, ShelfConfig
from kyra.io import ScenarioFrameSource
from kyra.manifest import ShapeFamily, TrackAnnotation, load_manifest, write_manifest
from kyra.pipeline import run_scenario
from kyra.simulation import (
    ScenarioCondition,
    ScenarioSettings,
    generate_scenario,
)

SIMULATION_CASES = (
    "suspicious-removal",
    "removal-without-person",
    "no-change",
    "person-without-removal",
    "addition",
    "authorized-restock",
    "occlusion-then-removal",
    "outside-association-window",
    "invalid-depth",
    "camera-drift",
)


def _write_result(payload: dict[str, Any], output: str | None = None) -> None:
    rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if output is not None:
        destination = Path(output)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(rendered, encoding="utf-8", newline="\n")
    sys.stdout.write(rendered)


def _settings(case: str, seed: int) -> ScenarioSettings:
    common = {
        "scenario_id": f"gate5-{case}",
        "random_seed": seed,
        "category": "gate5-test-object",
        "shape_family": ShapeFamily.THIN_BOX_OR_TRAY,
        "baseline_frame_count": 30,
    }
    if case in {
        "suspicious-removal",
        "removal-without-person",
        "occlusion-then-removal",
        "outside-association-window",
    }:
        return ScenarioSettings(
            **common,
            change_type=ChangeType.REMOVAL,
            should_alert=case in {"suspicious-removal", "occlusion-then-removal"},
            event_frame_count=(
                12 if case == "outside-association-window" else 9
                if case == "occlusion-then-removal"
                else 7
            ),
            frame_interval_ns=(
                500_000_000 if case == "outside-association-window" else 100_000_000
            ),
        )
    if case == "addition":
        return ScenarioSettings(
            **common,
            change_type=ChangeType.ADDITION,
            should_alert=False,
            event_frame_count=7,
        )
    if case == "authorized-restock":
        return ScenarioSettings(
            **common,
            change_type=ChangeType.ADDITION,
            should_alert=False,
            system_mode="RESTOCK_MODE",
            event_frame_count=7,
        )
    conditions = {
        "no-change": ScenarioCondition.NO_CHANGE,
        "person-without-removal": ScenarioCondition.NO_CHANGE,
        "invalid-depth": ScenarioCondition.INVALID_DEPTH,
        "camera-drift": ScenarioCondition.CAMERA_DRIFT,
    }
    return ScenarioSettings(
        **common,
        change_type=None,
        should_alert=False,
        condition=conditions[case],
        event_frame_count=7,
    )


def _add_initial_near_track(
    manifest_path: Path,
    *,
    occlude_object_region: bool = False,
) -> None:
    """Compose P1 scenario output with a P3 replay annotation for Gate 5."""

    manifest = load_manifest(manifest_path)
    baseline_ids = set(manifest.baseline_frame_ids)
    first_event = next(
        frame for frame in manifest.frames if frame.frame_id not in baseline_ids
    )
    _, _, width, height = manifest.shelf.roi_xyxy
    box_xyxy = (
        (0.2 * width, 0.2 * height, 0.8 * width, 0.8 * height)
        if occlude_object_region
        else (0.0, 0.0, 4.0, 4.0)
    )
    first_event.tracks = [
        TrackAnnotation(
            track_id=1,
            box_xyxy=box_xyxy,
            position_m=(0.0, 0.0, 1.0),
            near_shelf=True,
            authorized=False,
        )
    ]
    manifest.notes.append("gate5_profile=initial_near_non_authorized_track")
    write_manifest(manifest, manifest_path)


def _delay_removal(
    manifest_path: Path,
    *,
    unchanged_event_frames: int,
    profile: str,
) -> None:
    """Keep early event assets at baseline before exposing the removal."""

    manifest = load_manifest(manifest_path)
    root = manifest_path.parent
    baseline_ids = set(manifest.baseline_frame_ids)
    baseline = next(
        frame for frame in reversed(manifest.frames) if frame.frame_id in baseline_ids
    )
    event_frames = [
        frame for frame in manifest.frames if frame.frame_id not in baseline_ids
    ]
    for frame in event_frames[:unchanged_event_frames]:
        for field in (
            "rgb_path",
            "depth_path",
            "valid_mask_path",
            "occlusion_mask_path",
            "object_mask_path",
        ):
            source_path = getattr(baseline, field)
            destination_path = getattr(frame, field)
            if source_path is not None and destination_path is not None:
                shutil.copyfile(root / source_path, root / destination_path)
    manifest.ground_truth_events[0].first_seen_timestamp_ns = event_frames[
        unchanged_event_frames
    ].timestamp_ns
    manifest.notes.append(f"gate5_profile={profile}")
    write_manifest(manifest, manifest_path)


def _compose_timed_track(
    manifest_path: Path,
    *,
    unchanged_event_frames: int,
    profile: str,
    occlude_object_region: bool = False,
) -> None:
    _delay_removal(
        manifest_path,
        unchanged_event_frames=unchanged_event_frames,
        profile=profile,
    )
    _add_initial_near_track(
        manifest_path,
        occlude_object_region=occlude_object_region,
    )


def _make_restock_track_transient(manifest_path: Path) -> None:
    """Leave one authorized input track, then expose the addition for geometry."""

    manifest = load_manifest(manifest_path)
    baseline_ids = set(manifest.baseline_frame_ids)
    event_frames = [
        frame for frame in manifest.frames if frame.frame_id not in baseline_ids
    ]
    first_track = event_frames[0].tracks[0]
    first_track.box_xyxy = (0.0, 0.0, 4.0, 4.0)
    for frame in event_frames[1:]:
        frame.tracks = []
    manifest.notes.append("gate5_profile=transient_authorized_restock_track")
    write_manifest(manifest, manifest_path)


def generate_example_scenario(
    destination: str | Path,
    case: str = "suspicious-removal",
    *,
    seed: int = 42,
) -> Path:
    """Generate one reviewed synthetic profile for CLI or visual inspection."""

    if case not in SIMULATION_CASES:
        raise ValueError(f"unknown simulation case: {case!r}")
    manifest_path = generate_scenario(destination, _settings(case, seed))
    if case in {"suspicious-removal", "person-without-removal"}:
        _add_initial_near_track(manifest_path)
    elif case == "authorized-restock":
        _make_restock_track_transient(manifest_path)
    elif case == "occlusion-then-removal":
        _compose_timed_track(
            manifest_path,
            unchanged_event_frames=2,
            profile="temporary_occlusion_then_removal",
            occlude_object_region=True,
        )
    elif case == "outside-association-window":
        _compose_timed_track(
            manifest_path,
            unchanged_event_frames=5,
            profile="removal_after_association_window",
        )
    return manifest_path


def _simulate(args: argparse.Namespace) -> dict[str, Any]:
    manifest_path = generate_example_scenario(
        args.destination,
        args.case,
        seed=args.seed,
    )
    manifest = load_manifest(manifest_path)
    return {
        "command": "simulate",
        "scenario_id": manifest.scenario_id,
        "case": args.case,
        "evidence_source": manifest.evidence_source,
        "manifest_path": str(manifest_path.resolve()),
    }


def _calibrate(args: argparse.Namespace) -> dict[str, Any]:
    source = ScenarioFrameSource(args.manifest)
    shelf = source.manifest.shelf
    artifact = BaselineBuilder(
        minimum_frames=len(source.manifest.baseline_frame_ids)
    ).fit(source.baseline_frames(), ShelfConfig(**shelf.c007_values))
    npz_path, metadata_path = save_baseline(artifact, args.output)
    return {
        "command": "calibrate",
        "scenario_id": source.manifest.scenario_id,
        "calibration_checksum": artifact.calibration_checksum,
        "baseline_path": str(npz_path.resolve()),
        "metadata_path": str(metadata_path.resolve()),
    }


def _run(args: argparse.Namespace) -> dict[str, Any]:
    return {"command": "run", **run_scenario(args.manifest, baseline_path=args.baseline)}


def _evaluate(args: argparse.Namespace) -> dict[str, Any]:
    result = run_scenario(args.manifest, baseline_path=args.baseline)
    manifest = load_manifest(args.manifest)
    expected_types = sorted(event.change_type.value for event in manifest.ground_truth_events)
    actual_types = sorted(event["change_type"] for event in result["events"])
    expected_alert_count = sum(event.should_alert for event in manifest.ground_truth_events)
    actual_alert_count = int(result["alert_count"])
    passed = expected_types == actual_types and expected_alert_count == actual_alert_count
    return {
        "command": "evaluate",
        "scenario_id": manifest.scenario_id,
        "passed": passed,
        "expected_change_types": expected_types,
        "actual_change_types": actual_types,
        "expected_alert_count": expected_alert_count,
        "actual_alert_count": actual_alert_count,
    }


def _percentile(values: list[float], fraction: float) -> float:
    ordered = sorted(values)
    index = min(len(ordered) - 1, int((len(ordered) - 1) * fraction + 0.999999))
    return ordered[index]


def _benchmark(args: argparse.Namespace) -> dict[str, Any]:
    if args.runs < 1:
        raise ValueError("--runs must be positive")
    timings_ms: list[float] = []
    last_result: dict[str, Any] | None = None
    for _ in range(args.runs):
        started = perf_counter_ns()
        last_result = run_scenario(args.manifest, baseline_path=args.baseline)
        timings_ms.append((perf_counter_ns() - started) / 1_000_000)
    assert last_result is not None
    return {
        "command": "benchmark",
        "scenario_id": last_result["scenario_id"],
        "runs": args.runs,
        "p50_ms": _percentile(timings_ms, 0.50),
        "p95_ms": _percentile(timings_ms, 0.95),
        "min_ms": min(timings_ms),
        "max_ms": max(timings_ms),
        "event_frames_per_run": last_result["event_frames_processed"],
    }


def _demo(args: argparse.Namespace) -> dict[str, Any]:
    from kyra.demo import run_demo_scenario
    
    target = Path(args.destination)
    if target.is_dir() and (target / "scenario.json").exists():
        manifest_path = target / "scenario.json"
    elif target.is_file() and target.name == "scenario.json":
        manifest_path = target
    else:
        manifest_path = generate_example_scenario(
            args.destination,
            args.case,
            seed=42,
        )
        
    video_path = args.video if args.video else Path(args.destination) / "demo.mp4"
    result = run_demo_scenario(manifest_path, video_path)
    result["command"] = "demo"
    return result


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="kyra")
    subcommands = parser.add_subparsers(dest="command", required=True)

    simulate = subcommands.add_parser("simulate", help="generate a deterministic test scenario")
    simulate.add_argument("destination")
    simulate.add_argument("--case", choices=SIMULATION_CASES, default="suspicious-removal")
    simulate.add_argument("--seed", type=int, default=42)
    simulate.add_argument("--output", dest="report")
    simulate.set_defaults(handler=_simulate)

    calibrate = subcommands.add_parser("calibrate", help="build and save a shelf baseline")
    calibrate.add_argument("manifest")
    calibrate.add_argument("--output", required=True)
    calibrate.add_argument("--report")
    calibrate.set_defaults(handler=_calibrate)

    run = subcommands.add_parser("run", help="run the integrated scenario pipeline")
    run.add_argument("manifest")
    run.add_argument("--baseline")
    run.add_argument("--output", dest="report")
    run.set_defaults(handler=_run)

    evaluate = subcommands.add_parser("evaluate", help="compare inference with saved labels")
    evaluate.add_argument("manifest")
    evaluate.add_argument("--baseline")
    evaluate.add_argument("--output", dest="report")
    evaluate.set_defaults(handler=_evaluate)

    benchmark = subcommands.add_parser("benchmark", help="time repeated deterministic runs")
    benchmark.add_argument("manifest")
    benchmark.add_argument("--baseline")
    benchmark.add_argument("--runs", type=int, default=5)
    benchmark.add_argument("--output", dest="report")
    benchmark.set_defaults(handler=_benchmark)

    demo = subcommands.add_parser("demo", help="generate an annotated demo video")
    demo.add_argument("destination")
    demo.add_argument("--case", choices=SIMULATION_CASES, default="suspicious-removal")
    demo.add_argument("--video", help="output video path")
    demo.add_argument("--output", dest="report")
    demo.set_defaults(handler=_demo)

    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        payload = args.handler(args)
        _write_result(payload, getattr(args, "report", None))
        return 0 if payload.get("passed", True) else 1
    except (FileNotFoundError, FileExistsError, RuntimeError, ValueError) as error:
        sys.stderr.write(json.dumps({"error": str(error)}, sort_keys=True) + "\n")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

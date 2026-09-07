"""Generate the deterministic multi-frame synthetic Gate 6 split."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path

import cv2
import numpy as np

from kyra.contracts import ChangeType
from kyra.manifest import (
    ShapeFamily,
    TrackAnnotation,
    load_manifest,
    write_manifest,
)
from kyra.simulation import ScenarioCondition, ScenarioSettings, generate_scenario

GENERATOR_VERSION = "gate6-1.0"
CASES = (
    ("suspicious-removal", 6101),
    ("removal-without-person", 6102),
    ("person-without-removal", 6103),
    ("addition", 6104),
    ("authorized-restock", 6105),
    ("occlusion-then-removal", 6106),
    ("outside-association-window", 6107),
    ("invalid-depth", 6108),
    ("no-change", 6109),
    ("camera-drift", 6110),
)


def _settings(case: str, seed: int) -> ScenarioSettings:
    common = {
        "scenario_id": f"gate6-{case}",
        "random_seed": seed,
        "category": f"gate6-{case}",
        "shape_family": ShapeFamily.THIN_BOX_OR_TRAY,
        "baseline_frame_count": 30,
        "frame_interval_ns": 100_000_000,
        "split": "frozen_test",
    }
    if case in {"suspicious-removal", "removal-without-person"}:
        return ScenarioSettings(
            **common,
            change_type=ChangeType.REMOVAL,
            should_alert=case == "suspicious-removal",
            event_frame_count=7,
        )
    if case == "person-without-removal":
        return ScenarioSettings(
            **common,
            change_type=None,
            should_alert=False,
            condition=ScenarioCondition.NO_CHANGE,
            event_frame_count=7,
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
    if case == "occlusion-then-removal":
        return ScenarioSettings(
            **common,
            change_type=ChangeType.REMOVAL,
            should_alert=True,
            event_frame_count=9,
        )
    if case == "outside-association-window":
        return ScenarioSettings(
            **common,
            change_type=ChangeType.REMOVAL,
            should_alert=False,
            event_frame_count=28,
        )
    condition = {
        "invalid-depth": ScenarioCondition.INVALID_DEPTH,
        "no-change": ScenarioCondition.NO_CHANGE,
        "camera-drift": ScenarioCondition.CAMERA_DRIFT,
    }[case]
    return ScenarioSettings(
        **common,
        change_type=None,
        should_alert=False,
        condition=condition,
        event_frame_count=7,
    )


def _add_track(manifest_path: Path, *, authorized: bool = False) -> None:
    manifest = load_manifest(manifest_path)
    baseline_ids = set(manifest.baseline_frame_ids)
    first_event = next(frame for frame in manifest.frames if frame.frame_id not in baseline_ids)
    first_event.tracks = [
        TrackAnnotation(
            track_id=1,
            box_xyxy=(0.0, 0.0, 4.0, 4.0),
            position_m=(0.0, 0.0, 1.0),
            near_shelf=True,
            authorized=authorized,
        )
    ]
    write_manifest(manifest, manifest_path)


def _delay_removal(manifest_path: Path, unchanged_event_frames: int) -> None:
    manifest = load_manifest(manifest_path)
    root = manifest_path.parent
    baseline_ids = set(manifest.baseline_frame_ids)
    baseline = next(frame for frame in reversed(manifest.frames) if frame.frame_id in baseline_ids)
    event_frames = [frame for frame in manifest.frames if frame.frame_id not in baseline_ids]
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
    write_manifest(manifest, manifest_path)


def _occlude_tail(manifest_path: Path, tail_frames: int) -> None:
    manifest = load_manifest(manifest_path)
    root = manifest_path.parent
    event_frames = [
        frame for frame in manifest.frames if frame.frame_id not in manifest.baseline_frame_ids
    ]
    for frame in event_frames[-tail_frames:]:
        if frame.object_mask_path is None or frame.occlusion_mask_path is None:
            raise ValueError("Gate 6 occlusion scenario requires mask paths")
        object_mask = cv2.imread(
            str(root / frame.object_mask_path), cv2.IMREAD_GRAYSCALE
        )
        if object_mask is None:
            raise FileNotFoundError(frame.object_mask_path)
        occlusion_mask = cv2.dilate(
            object_mask,
            np.ones((7, 7), dtype=np.uint8),
            iterations=1,
        )
        if not cv2.imwrite(str(root / frame.occlusion_mask_path), occlusion_mask):
            raise RuntimeError(f"could not write {frame.occlusion_mask_path}")
    write_manifest(manifest, manifest_path)


def _make_restock_track_transient(manifest_path: Path) -> None:
    manifest = load_manifest(manifest_path)
    event_frames = [
        frame for frame in manifest.frames if frame.frame_id not in manifest.baseline_frame_ids
    ]
    event_frames[0].tracks = [
        TrackAnnotation(
            track_id=1,
            box_xyxy=(0.0, 0.0, 4.0, 4.0),
            position_m=(0.0, 0.0, 1.0),
            near_shelf=True,
            authorized=True,
        )
    ]
    for frame in event_frames[1:]:
        frame.tracks = []
    write_manifest(manifest, manifest_path)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def generate_split(destination: str | Path) -> Path:
    root = Path(destination)
    if root.exists() and any(root.iterdir()):
        raise FileExistsError(f"Gate 6 output folder is not empty: {root}")
    root.mkdir(parents=True, exist_ok=True)
    entries: list[dict[str, object]] = []
    for case, seed in CASES:
        scenario_root = root / case
        manifest_path = generate_scenario(scenario_root, _settings(case, seed))
        if case in {"suspicious-removal", "person-without-removal"}:
            _add_track(manifest_path)
        elif case == "authorized-restock":
            _make_restock_track_transient(manifest_path)
        elif case == "occlusion-then-removal":
            _add_track(manifest_path)
            _occlude_tail(manifest_path, tail_frames=2)
        elif case == "outside-association-window":
            _delay_removal(manifest_path, unchanged_event_frames=21)
            _add_track(manifest_path)
        manifest = load_manifest(manifest_path)
        entries.append(
            {
                "scenario_id": manifest.scenario_id,
                "case": case,
                "seed": seed,
                "manifest_path": manifest_path.relative_to(root).as_posix(),
                "expected_event_types": sorted(
                    event.change_type.value for event in manifest.ground_truth_events
                ),
                "expected_alert": any(
                    event.should_alert for event in manifest.ground_truth_events
                ),
            }
        )
    index = {
        "schema_version": "1.0",
        "split_id": "gate6-synthetic-v1",
        "status": "prepared_pending_owner_freeze",
        "evidence_source": "synthetic",
        "generator_version": GENERATOR_VERSION,
        "baseline_frame_count": 30,
        "minimum_event_frame_count": 7,
        "frame_interval_ns": 100_000_000,
        "scenario_count": len(entries),
        "scenarios": entries,
    }
    (root / "gate6.json").write_text(
        json.dumps(index, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    inventory = {
        path.relative_to(root).as_posix(): _sha256(path)
        for path in sorted(root.rglob("*"))
        if path.is_file() and path.name != "checksums.sha256"
    }
    (root / "checksums.sha256").write_text(
        "".join(f"{digest}  {path}\n" for path, digest in inventory.items()),
        encoding="utf-8",
        newline="\n",
    )
    return root


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination")
    args = parser.parse_args()
    generate_split(args.destination)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
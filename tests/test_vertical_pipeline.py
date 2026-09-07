from __future__ import annotations

import json
from pathlib import Path

import pytest

from kyra.cli import main
from kyra.pipeline import run_scenario


def _run_cli(capsys, *args: str) -> dict[str, object]:
    assert main(list(args)) == 0
    return json.loads(capsys.readouterr().out)


def test_five_command_cli_runs_suspicious_removal_end_to_end(
    tmp_path: Path,
    capsys,
) -> None:
    scenario_dir = tmp_path / "suspicious-removal"
    baseline_path = tmp_path / "baseline.npz"

    simulated = _run_cli(
        capsys,
        "simulate",
        str(scenario_dir),
        "--case",
        "suspicious-removal",
    )
    manifest_path = Path(str(simulated["manifest_path"]))
    assert manifest_path.is_file()

    calibrated = _run_cli(
        capsys,
        "calibrate",
        str(manifest_path),
        "--output",
        str(baseline_path),
    )
    assert calibrated["calibration_checksum"]
    assert baseline_path.is_file()

    result = _run_cli(
        capsys,
        "run",
        str(manifest_path),
        "--baseline",
        str(baseline_path),
    )
    assert result["event_count"] == 1
    assert result["manifest_path"] == str(manifest_path.resolve())
    assert result["shelf_config"]["shelf_id"] == "shelf-01"
    assert result["events"][0]["change_type"] == "REMOVAL"
    assert result["alert_count"] == 1
    assert result["alerts"][0]["person_track_id"] == 1
    assert result["alerts"][0]["volume_event_id"] == result["events"][0]["event_id"]

    evaluation = _run_cli(
        capsys,
        "evaluate",
        str(manifest_path),
        "--baseline",
        str(baseline_path),
    )
    assert evaluation["passed"] is True
    assert evaluation["expected_alert_count"] == 1
    assert evaluation["actual_alert_count"] == 1

    benchmark = _run_cli(
        capsys,
        "benchmark",
        str(manifest_path),
        "--baseline",
        str(baseline_path),
        "--runs",
        "2",
    )
    assert benchmark["runs"] == 2
    assert benchmark["p50_ms"] > 0
    assert benchmark["p95_ms"] >= benchmark["p50_ms"]


def test_removal_without_person_produces_event_but_no_alert(
    tmp_path: Path,
    capsys,
) -> None:
    scenario_dir = tmp_path / "removal-without-person"
    manifest_path = Path(
        str(
            _run_cli(
                capsys,
                "simulate",
                str(scenario_dir),
                "--case",
                "removal-without-person",
            )["manifest_path"]
        )
    )

    result = run_scenario(manifest_path)

    assert result["event_count"] == 1
    assert result["alert_count"] == 0


def test_invalid_depth_is_unknown_and_does_not_alert(tmp_path: Path, capsys) -> None:
    scenario_dir = tmp_path / "invalid-depth"
    manifest_path = Path(
        str(
            _run_cli(
                capsys,
                "simulate",
                str(scenario_dir),
                "--case",
                "invalid-depth",
            )["manifest_path"]
        )
    )

    result = run_scenario(manifest_path)

    assert result["event_count"] == 0
    assert result["alert_count"] == 0


def test_run_does_not_use_ground_truth_labels_for_inference(
    tmp_path: Path,
    capsys,
) -> None:
    scenario_dir = tmp_path / "ground-truth-boundary"
    manifest_path = Path(
        str(
            _run_cli(
                capsys,
                "simulate",
                str(scenario_dir),
                "--case",
                "suspicious-removal",
            )["manifest_path"]
        )
    )
    original = run_scenario(manifest_path)
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    payload["ground_truth_events"] = []
    manifest_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    without_labels = run_scenario(manifest_path)

    assert without_labels["events"] == original["events"]
    assert without_labels["alerts"] == original["alerts"]


@pytest.mark.parametrize(
    "case",
    [
        "removal-without-person",
        "no-change",
        "person-without-removal",
        "addition",
        "authorized-restock",
        "outside-association-window",
        "invalid-depth",
    ],
)
def test_safe_scenario_profiles_evaluate_without_false_alerts(
    case: str,
    tmp_path: Path,
    capsys,
) -> None:
    scenario_dir = tmp_path / case
    manifest_path = Path(
        str(
            _run_cli(
                capsys,
                "simulate",
                str(scenario_dir),
                "--case",
                case,
            )["manifest_path"]
        )
    )

    evaluation = _run_cli(capsys, "evaluate", str(manifest_path))

    assert evaluation["passed"] is True
    assert evaluation["actual_alert_count"] == 0


def test_temporary_occlusion_then_removal_alerts_once(
    tmp_path: Path,
    capsys,
) -> None:
    scenario_dir = tmp_path / "occlusion-then-removal"
    manifest_path = Path(
        str(
            _run_cli(
                capsys,
                "simulate",
                str(scenario_dir),
                "--case",
                "occlusion-then-removal",
            )["manifest_path"]
        )
    )

    evaluation = _run_cli(capsys, "evaluate", str(manifest_path))

    assert evaluation["passed"] is True
    assert evaluation["actual_change_types"] == ["REMOVAL"]
    assert evaluation["actual_alert_count"] == 1


def test_camera_drift_does_not_produce_false_removal(
    tmp_path: Path,
    capsys,
) -> None:
    scenario_dir = tmp_path / "camera-drift"
    manifest_path = Path(
        str(
            _run_cli(
                capsys,
                "simulate",
                str(scenario_dir),
                "--case",
                "camera-drift",
            )["manifest_path"]
        )
    )

    assert main(["evaluate", str(manifest_path)]) == 0
    evaluation = json.loads(capsys.readouterr().out)

    assert evaluation["passed"] is True
    assert evaluation["expected_change_types"] == []
    assert evaluation["actual_change_types"] == []
    assert evaluation["actual_alert_count"] == 0

"""Deterministic Gate 6 evaluation over a frozen scenario split."""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from kyra.manifest import ScenarioManifest, load_manifest
from kyra.pipeline import run_scenario

SPLIT_SCHEMA_VERSION = "1.0"
CHECKSUMS_NAME = "checksums.sha256"
EXCLUDED_METRICS = {
    "track_association": "ground-truth associated track IDs are not supplied",
    "live_tracker_accuracy": "the optional live tracker is not evaluated",
    "public_ocid_accuracy": "public OCID data is outside this synthetic split",
    "real_world_calibration": "synthetic replay is not real-world calibration evidence",
}
SECTION_10_REQUIREMENTS = {
    "geometry_balanced_accuracy": {"threshold": 0.90, "comparison": ">"},
    "theft_rule_recall": {
        "threshold": 0.92,
        "minimum_correct": 111,
        "required_trials": 120,
        "comparison": ">",
    },
    "false_positive_rate": {
        "threshold": 0.011,
        "maximum_false_alerts": 3,
        "required_trials": 300,
        "comparison": "<",
    },
}


class Gate6EvaluationError(ValueError):
    """Raised when a Gate 6 split or evaluation input is invalid."""


@dataclass(frozen=True, slots=True)
class EvaluationConfig:
    """Evaluation settings; omitted acceptance thresholds remain pending."""

    timing_tolerance_ns: int | None = None
    volume_error_threshold: float | None = None
    bounds_iou_threshold: float | None = None

    def __post_init__(self) -> None:
        if self.timing_tolerance_ns is not None and self.timing_tolerance_ns < 0:
            raise ValueError("timing tolerance must be non-negative")
        if self.volume_error_threshold is not None and self.volume_error_threshold < 0:
            raise ValueError("volume error threshold must be non-negative")
        if self.bounds_iou_threshold is not None and not 0 <= self.bounds_iou_threshold <= 1:
            raise ValueError("bounds IoU threshold must be between zero and one")

    def as_dict(self) -> dict[str, int | float | None]:
        return {
            "timing_tolerance_ns": self.timing_tolerance_ns,
            "volume_error_threshold": self.volume_error_threshold,
            "bounds_iou_threshold": self.bounds_iou_threshold,
        }


TEXT_ASSET_SUFFIXES = {".json", ".toml", ".sha256", ".md", ".txt"}


def _sha256(path: Path) -> str:
    data = path.read_bytes()
    if path.suffix in TEXT_ASSET_SUFFIXES:
        data = data.replace(b"\r\n", b"\n")
    return hashlib.sha256(data).hexdigest()


def _inventory(root: Path) -> dict[str, str]:
    return {
        path.relative_to(root).as_posix(): _sha256(path)
        for path in sorted(root.rglob("*"))
        if path.is_file() and path.name != CHECKSUMS_NAME
    }


def _recorded_inventory(root: Path) -> dict[str, str]:
    checksum_path = root / CHECKSUMS_NAME
    if not checksum_path.is_file():
        raise Gate6EvaluationError(f"missing checksum inventory: {checksum_path}")
    records: dict[str, str] = {}
    for line in checksum_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            digest, relative_path = line.split("  ", maxsplit=1)
        except ValueError as error:
            raise Gate6EvaluationError(f"malformed checksum line: {line!r}") from error
        records[relative_path] = digest
    return records


def _load_index(root: Path) -> dict[str, Any]:
    index_path = root / "gate6.json"
    if not index_path.is_file():
        raise Gate6EvaluationError(f"missing Gate 6 split index: {index_path}")
    try:
        index = json.loads(index_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise Gate6EvaluationError(f"invalid Gate 6 split index: {index_path}") from error
    if index.get("schema_version") != SPLIT_SCHEMA_VERSION:
        raise Gate6EvaluationError("unsupported Gate 6 split index version")
    if index.get("evidence_source") != "synthetic":
        raise Gate6EvaluationError("Gate 6 implementation accepts synthetic evidence only")
    scenarios = index.get("scenarios")
    if not isinstance(scenarios, list) or not scenarios:
        raise Gate6EvaluationError("Gate 6 split must contain scenarios")
    if index.get("baseline_frame_count") != 30:
        raise Gate6EvaluationError("Gate 6 index must require 30 baseline frames")
    if index.get("minimum_event_frame_count") != 7:
        raise Gate6EvaluationError("Gate 6 index must require 7 event frames")
    if index.get("frame_interval_ns") != 100_000_000:
        raise Gate6EvaluationError("Gate 6 index must require 100 ms frame spacing")
    return index


def load_gate6_split(root: str | Path) -> tuple[Path, dict[str, Any], tuple[ScenarioManifest, ...]]:
    """Load and validate a checksumed Gate 6 scenario split."""

    split_root = Path(root).resolve()
    if not split_root.is_dir():
        raise Gate6EvaluationError(f"Gate 6 split directory does not exist: {split_root}")
    index = _load_index(split_root)
    recorded = _recorded_inventory(split_root)
    actual = _inventory(split_root)
    if recorded != actual:
        raise Gate6EvaluationError("Gate 6 checksum inventory does not match split files")

    manifests: list[ScenarioManifest] = []
    scenario_ids: set[str] = set()
    for entry in index["scenarios"]:
        if not isinstance(entry, dict):
            raise Gate6EvaluationError("Gate 6 scenario entry must be an object")
        relative_path = entry.get("manifest_path")
        if not isinstance(relative_path, str) or Path(relative_path).is_absolute():
            raise Gate6EvaluationError("Gate 6 manifest paths must be relative")
        manifest_path = (split_root / relative_path).resolve()
        try:
            manifest_path.relative_to(split_root)
        except ValueError as error:
            raise Gate6EvaluationError("Gate 6 manifest path escapes split directory") from error
        if not manifest_path.is_file():
            raise Gate6EvaluationError(f"missing Gate 6 manifest: {manifest_path}")
        manifest = load_manifest(manifest_path)
        if manifest.split != "frozen_test":
            raise Gate6EvaluationError(f"manifest is not frozen_test: {manifest.scenario_id}")
        if manifest.evidence_source != "synthetic":
            raise Gate6EvaluationError(f"manifest is not synthetic: {manifest.scenario_id}")
        event_frame_count = len(manifest.frames) - len(manifest.baseline_frame_ids)
        if len(manifest.baseline_frame_ids) != index["baseline_frame_count"]:
            raise Gate6EvaluationError(
                f"{manifest.scenario_id} does not have exactly 30 baseline frames"
            )
        if event_frame_count < index["minimum_event_frame_count"]:
            raise Gate6EvaluationError(
                f"{manifest.scenario_id} does not have at least 7 event frames"
            )
        timestamps = [frame.timestamp_ns for frame in manifest.frames]
        if any(
            later - earlier != index["frame_interval_ns"]
            for earlier, later in zip(timestamps, timestamps[1:], strict=False)
        ):
            raise Gate6EvaluationError(
                f"{manifest.scenario_id} does not use 100 ms frame spacing"
            )
        if len(manifest.ground_truth_events) > 1:
            raise Gate6EvaluationError(
                f"{manifest.scenario_id} contains unsupported multiple ground-truth events"
            )
        if entry.get("scenario_id") != manifest.scenario_id:
            raise Gate6EvaluationError(
                f"scenario ID mismatch for {entry.get('manifest_path')!r}"
            )
        if entry.get("seed") != manifest.random_seed:
            raise Gate6EvaluationError(f"seed mismatch for {manifest.scenario_id}")
        expected_types = sorted(
            event.change_type.value for event in manifest.ground_truth_events
        )
        if entry.get("expected_event_types") != expected_types:
            raise Gate6EvaluationError(
                f"expected event metadata mismatch for {manifest.scenario_id}"
            )
        expected_alert = any(event.should_alert for event in manifest.ground_truth_events)
        if entry.get("expected_alert") is not expected_alert:
            raise Gate6EvaluationError(
                f"expected alert metadata mismatch for {manifest.scenario_id}"
            )
        if manifest.scenario_id in scenario_ids:
            raise Gate6EvaluationError(f"duplicate Gate 6 scenario: {manifest.scenario_id}")
        scenario_ids.add(manifest.scenario_id)
        manifests.append(manifest)

    if index.get("scenario_count") != len(manifests):
        raise Gate6EvaluationError("Gate 6 scenario count does not match manifests")
    return split_root, index, tuple(manifests)


def _bounds_iou(
    first_min: tuple[float, float, float],
    first_max: tuple[float, float, float],
    second_min: tuple[float, float, float],
    second_max: tuple[float, float, float],
) -> float:
    intersection = 1.0
    first_volume = 1.0
    second_volume = 1.0
    for axis in range(3):
        intersection *= max(
            0.0,
            min(first_max[axis], second_max[axis])
            - max(first_min[axis], second_min[axis]),
        )
        first_volume *= max(0.0, first_max[axis] - first_min[axis])
        second_volume *= max(0.0, second_max[axis] - second_min[axis])
    union = first_volume + second_volume - intersection
    return intersection / union if union else 0.0


def _counts(expected: bool, actual: bool) -> dict[str, int]:
    return {
        "tp": int(expected and actual),
        "fp": int(not expected and actual),
        "fn": int(expected and not actual),
    }


def _merge_counts(rows: list[dict[str, int]]) -> dict[str, int]:
    return {name: sum(row[name] for row in rows) for name in ("tp", "fp", "fn")}


def _classification(counts: dict[str, int]) -> dict[str, float | None]:
    tp, fp, fn = counts["tp"], counts["fp"], counts["fn"]
    precision = tp / (tp + fp) if tp + fp else None
    recall = tp / (tp + fn) if tp + fn else None
    f1 = (
        2 * precision * recall / (precision + recall)
        if precision is not None and recall is not None and precision + recall
        else None
    )
    return {"precision": precision, "recall": recall, "f1": f1}


def _binomial_interval(successes: int, trials: int) -> dict[str, float | None]:
    """Return a two-sided 95% Wilson interval for a binomial proportion."""

    if trials == 0:
        return {"point": None, "lower": None, "upper": None, "successes": 0, "trials": 0}
    z = 1.959963984540054
    proportion = successes / trials
    denominator = 1.0 + z**2 / trials
    centre = proportion + z**2 / (2.0 * trials)
    margin = z * math.sqrt(
        proportion * (1.0 - proportion) / trials + z**2 / (4.0 * trials**2)
    )
    return {
        "point": proportion,
        "lower": max(0.0, (centre - margin) / denominator),
        "upper": min(1.0, (centre + margin) / denominator),
        "successes": successes,
        "trials": trials,
    }


def _current_scope_metrics(rows: list[dict[str, Any]]) -> dict[str, Any]:
    removal_rows = [row for row in rows if row["expected_event_types"] == ["REMOVAL"]]
    non_removal_rows = [row for row in rows if row["expected_event_types"] != ["REMOVAL"]]
    removal_correct = sum(row["actual_event_types"] == ["REMOVAL"] for row in removal_rows)
    non_removal_correct = sum(row["actual_event_types"] != ["REMOVAL"] for row in non_removal_rows)
    balanced_accuracy = None
    if removal_rows and non_removal_rows:
        balanced_accuracy = (
            removal_correct / len(removal_rows)
            + non_removal_correct / len(non_removal_rows)
        ) / 2.0

    removed_components = len(removal_rows)
    detected_components = removal_correct
    volume_errors = [
        row["volume_relative_error"]
        for row in removal_rows
        if row.get("volume_relative_error") is not None
    ]
    sorted_volume_errors = sorted(volume_errors)
    median_volume_error = None
    if sorted_volume_errors:
        midpoint = len(sorted_volume_errors) // 2
        median_volume_error = sorted_volume_errors[midpoint]
        if len(sorted_volume_errors) % 2 == 0:
            median_volume_error = (
                sorted_volume_errors[midpoint - 1] + sorted_volume_errors[midpoint]
            ) / 2.0
    alert_positive_rows = [row for row in rows if row["expected_alert"]]
    alert_negative_rows = [row for row in rows if not row["expected_alert"]]
    correct_alerts = sum(row["actual_alert"] for row in alert_positive_rows)
    false_alerts = sum(row["actual_alert"] for row in alert_negative_rows)

    return {
        "geometry_balanced_accuracy": {
            "point": balanced_accuracy,
            "removal_correct": removal_correct,
            "removal_trials": len(removal_rows),
            "non_removal_correct": non_removal_correct,
            "non_removal_trials": len(non_removal_rows),
            "section_10_status": "current_validation_only",
        },
        "missing_volume_recall": {
            "point": detected_components / removed_components if removed_components else None,
            "detected_components": detected_components,
            "labeled_removed_components": removed_components,
            "section_10_status": "reported_no_numeric_threshold",
        },
        "volume_error": {
            "median_absolute_percentage_error": (
                median_volume_error * 100.0
                if median_volume_error is not None
                else None
            ),
            "applicable_trials": len(volume_errors),
            "section_10_status": "reported_no_numeric_threshold",
        },
        "theft_rule_recall": {
            **_binomial_interval(correct_alerts, len(alert_positive_rows)),
            "section_10_status": "unavailable_final_dataset",
        },
        "false_positive_rate": {
            "false_alerts": false_alerts,
            **_binomial_interval(false_alerts, len(alert_negative_rows)),
            "section_10_status": "unavailable_final_dataset",
        },
        "latency": {
            "stage": {"status": "unavailable_no_stage_instrumentation"},
            "complete_pipeline": {
                "status": "available_via_benchmark_command",
                "command": "kyra benchmark <manifest> --runs 5",
            },
        },
    }


def _event_labels(manifest: ScenarioManifest) -> list[str]:
    return sorted(event.change_type.value for event in manifest.ground_truth_events)


def _event_counts(expected_label: str, actual_label: str) -> dict[str, int]:
    if expected_label == actual_label and expected_label != "NO_EVENT":
        return {"tp": 1, "fp": 0, "fn": 0}
    return {
        "tp": 0,
        "fp": int(actual_label != "NO_EVENT"),
        "fn": int(expected_label != "NO_EVENT"),
    }


def _score_scenario(
    manifest: ScenarioManifest,
    result: dict[str, Any],
    entry: dict[str, Any],
    settings: EvaluationConfig,
) -> tuple[dict[str, Any], dict[str, int], dict[str, int], dict[str, int]]:
    expected_events = _event_labels(manifest)
    actual_events = sorted(event["change_type"] for event in result["events"])
    if len(actual_events) > 1:
        raise Gate6EvaluationError(
            f"{manifest.scenario_id} produced unsupported multiple events"
        )
    expected_label = expected_events[0] if expected_events else "NO_EVENT"
    actual_label = actual_events[0] if actual_events else "NO_EVENT"
    expected_event = expected_label != "NO_EVENT"
    actual_event = actual_label != "NO_EVENT"
    expected_alert = any(event.should_alert for event in manifest.ground_truth_events)
    actual_alert = bool(result["alerts"])
    event_count = _event_counts(expected_label, actual_label)
    event_presence_count = _counts(expected_event, actual_event)
    alert_count = _counts(expected_alert, actual_alert)
    row: dict[str, Any] = {
        "scenario_id": manifest.scenario_id,
        "manifest_path": entry["manifest_path"],
        "evidence_source": manifest.evidence_source,
        "expected_event_types": expected_events,
        "actual_event_types": actual_events,
        "expected_alert": expected_alert,
        "actual_alert": actual_alert,
        "event_counts": event_count,
        "event_presence_counts": event_presence_count,
        "alert_counts": alert_count,
        "event_pass": expected_events == actual_events,
        "alert_pass": expected_alert == actual_alert,
        "baseline_checksum": result["baseline_checksum"],
        "event_frames_processed": result["event_frames_processed"],
    }
    if len(manifest.ground_truth_events) == 1 and len(result["events"]) == 1:
        expected = manifest.ground_truth_events[0]
        actual = result["events"][0]
        row["detection_timing_ns"] = (
            actual["first_seen_timestamp_ns"] - expected.first_seen_timestamp_ns
        )
        if expected.volume_m3 > 0:
            row["volume_relative_error"] = (
                abs(actual["missing_volume_m3"] - expected.volume_m3)
                / expected.volume_m3
            )
        if expected.bounds_min_m is not None and expected.bounds_max_m is not None:
            row["bounds_iou"] = _bounds_iou(
                expected.bounds_min_m,
                expected.bounds_max_m,
                tuple(actual["bounds_min_m"]),
                tuple(actual["bounds_max_m"]),
            )
    threshold_checks: dict[str, bool] = {}
    if settings.timing_tolerance_ns is not None and "detection_timing_ns" in row:
        threshold_checks["timing"] = abs(row["detection_timing_ns"]) <= settings.timing_tolerance_ns
    if settings.volume_error_threshold is not None and "volume_relative_error" in row:
        threshold_checks["volume"] = row["volume_relative_error"] <= settings.volume_error_threshold
    if settings.bounds_iou_threshold is not None and "bounds_iou" in row:
        threshold_checks["bounds"] = row["bounds_iou"] >= settings.bounds_iou_threshold
    row["threshold_checks"] = threshold_checks
    return row, event_count, event_presence_count, alert_count


def evaluate_split(
    root: str | Path,
    *,
    config: EvaluationConfig | None = None,
) -> dict[str, Any]:
    """Evaluate every scenario in a validated Gate 6 split."""

    split_root, index, manifests = load_gate6_split(root)
    settings = config or EvaluationConfig()
    scenario_rows: list[dict[str, Any]] = []
    event_counts: list[dict[str, int]] = []
    event_presence_counts: list[dict[str, int]] = []
    alert_counts: list[dict[str, int]] = []
    event_confusion: dict[str, dict[str, int]] = {}
    alert_confusion: dict[str, dict[str, int]] = {}
    for entry, manifest in zip(index["scenarios"], manifests, strict=True):
        manifest_path = split_root / entry["manifest_path"]
        result = run_scenario(manifest_path)
        row, event_count, event_presence_count, alert_count = _score_scenario(
            manifest, result, entry, settings
        )
        expected_events = row["expected_event_types"]
        actual_events = row["actual_event_types"]
        expected_alert = row["expected_alert"]
        actual_alert = row["actual_alert"]
        event_counts.append(event_count)
        event_presence_counts.append(event_presence_count)
        alert_counts.append(alert_count)
        expected_label = expected_events[0] if expected_events else "NO_EVENT"
        actual_label = actual_events[0] if actual_events else "NO_EVENT"
        event_confusion.setdefault(expected_label, {})[actual_label] = (
            event_confusion.setdefault(expected_label, {}).get(actual_label, 0) + 1
        )
        expected_alert_label = "ALERT" if expected_alert else "NO_ALERT"
        actual_alert_label = "ALERT" if actual_alert else "NO_ALERT"
        alert_confusion.setdefault(expected_alert_label, {})[actual_alert_label] = (
            alert_confusion.setdefault(expected_alert_label, {}).get(actual_alert_label, 0) + 1
        )

        scenario_rows.append(row)

    merged_events = _merge_counts(event_counts)
    merged_alerts = _merge_counts(alert_counts)
    current_metrics = _current_scope_metrics(scenario_rows)
    threshold_values = {
        "timing": settings.timing_tolerance_ns,
        "volume": settings.volume_error_threshold,
        "bounds": settings.bounds_iou_threshold,
    }
    configured_names = {
        name for name, value in threshold_values.items() if value is not None
    }
    threshold_status = {
        name: "configured" if value is not None else "not_configured"
        for name, value in threshold_values.items()
    }
    if not configured_names:
        threshold_overall = "no_thresholds_configured"
    elif len(configured_names) < 3:
        threshold_overall = "partially_configured"
    else:
        applicable_counts = {
            name: sum(name in row["threshold_checks"] for row in scenario_rows)
            for name in configured_names
        }
        all_applicable = all(count > 0 for count in applicable_counts.values())
        all_checks_pass = all(
            check
            for row in scenario_rows
            for check in row["threshold_checks"].values()
        )
        threshold_overall = (
            "all_thresholds_passed"
            if all_applicable and all_checks_pass
            else "all_thresholds_failed" if all_applicable else "all_thresholds_not_evaluable"
        )
    threshold_status["overall"] = threshold_overall
    if threshold_overall == "all_thresholds_passed":
        acceptance_status = "passed"
    elif threshold_overall == "all_thresholds_failed":
        acceptance_status = "failed"
    else:
        acceptance_status = "pending"
    return {
        "evaluation": "gate6",
        "split_id": index["split_id"],
        "split_status": index.get("status"),
        "generator_version": index.get("generator_version"),
        "fixture_inventory_sha256": _sha256(split_root / CHECKSUMS_NAME),
        "scenario_count": len(scenario_rows),
        "configuration": settings.as_dict(),
        "threshold_status": threshold_status,
        "scenarios": scenario_rows,
        "event": {"counts": merged_events, **_classification(merged_events)},
        "event_presence": {
            "counts": _merge_counts(event_presence_counts),
            **_classification(_merge_counts(event_presence_counts)),
        },
        "alert": {"counts": merged_alerts, **_classification(merged_alerts)},
        "current_scope_metrics": current_metrics,
        "section_10_requirements": SECTION_10_REQUIREMENTS,
        "event_confusion_matrix": event_confusion,
        "alert_confusion_matrix": alert_confusion,
        "excluded_metrics": EXCLUDED_METRICS,
        "comparison_baseline": None,
        "acceptance_status": acceptance_status,
        "section_10_acceptance_status": "unavailable_final_dataset",
    }

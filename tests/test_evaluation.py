from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path
from types import SimpleNamespace

import pytest

from kyra.contracts import ChangeType
from kyra.evaluation import EvaluationConfig, Gate6EvaluationError, evaluate_split, load_gate6_split
from kyra.evaluation.gate6 import _classification, _score_scenario

SPLIT_ROOT = Path(__file__).parents[1] / "scenario-fixtures" / "gate6"


def _manifest(change_type: ChangeType | None, should_alert: bool = False):
    events = []
    if change_type is not None:
        events.append(
            SimpleNamespace(
                change_type=change_type,
                should_alert=should_alert,
                first_seen_timestamp_ns=100,
                volume_m3=2.0,
                bounds_min_m=(0.0, 0.0, 0.0),
                bounds_max_m=(1.0, 1.0, 1.0),
            )
        )
    return SimpleNamespace(
        scenario_id="synthetic-test",
        evidence_source="synthetic",
        ground_truth_events=events,
    )


def _result(
    change_type: str | None,
    *,
    alert: bool = False,
    first_seen_timestamp_ns: int = 100,
    volume_m3: float = 2.0,
    bounds_min_m: tuple[float, float, float] = (0.0, 0.0, 0.0),
    bounds_max_m: tuple[float, float, float] = (1.0, 1.0, 1.0),
):
    events = []
    if change_type is not None:
        events.append(
            {
                "change_type": change_type,
                "first_seen_timestamp_ns": first_seen_timestamp_ns,
                "missing_volume_m3": volume_m3,
                "bounds_min_m": bounds_min_m,
                "bounds_max_m": bounds_max_m,
            }
        )
    return {
        "events": events,
        "alerts": [{}] if alert else [],
        "baseline_checksum": "a" * 64,
        "event_frames_processed": 7,
    }


def _entry() -> dict[str, object]:
    return {"manifest_path": "synthetic/scenario.json"}


def _refresh_checksums(root: Path) -> None:
    records = []
    for path in sorted(root.rglob("*")):
        if path.is_file() and path.name != "checksums.sha256":
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            records.append(f"{digest}  {path.relative_to(root).as_posix()}\n")
    (root / "checksums.sha256").write_text("".join(records), encoding="utf-8")


def test_gate6_split_scores_positive_event_and_alert() -> None:
    result = evaluate_split(SPLIT_ROOT)

    row = next(
        row
        for row in result["scenarios"]
        if row["scenario_id"] == "gate6-suspicious-removal"
    )
    assert row["event_pass"] is True
    assert row["alert_pass"] is True
    assert result["event"]["counts"] == {"tp": 6, "fp": 0, "fn": 0}
    assert result["alert"]["counts"] == {"tp": 2, "fp": 0, "fn": 0}


def test_gate6_split_scores_event_without_alert_and_negative_cases() -> None:
    result = evaluate_split(SPLIT_ROOT)

    removal_without_person = next(
        row for row in result["scenarios"] if row["scenario_id"] == "gate6-removal-without-person"
    )
    no_change = next(row for row in result["scenarios"] if row["scenario_id"] == "gate6-no-change")
    assert removal_without_person["event_pass"] is True
    assert removal_without_person["alert_pass"] is True
    assert no_change["event_counts"] == {"tp": 0, "fp": 0, "fn": 0}
    assert no_change["alert_counts"] == {"tp": 0, "fp": 0, "fn": 0}


def test_gate6_split_has_expected_aggregate_metrics() -> None:
    result = evaluate_split(SPLIT_ROOT)

    assert result["event"]["counts"] == {"tp": 6, "fp": 0, "fn": 0}
    assert result["alert"]["counts"] == {"tp": 2, "fp": 0, "fn": 0}
    assert result["event"]["precision"] == 1.0
    assert result["event"]["recall"] == 1.0
    assert result["event"]["f1"] == 1.0
    assert result["event_presence"]["counts"] == {"tp": 6, "fp": 0, "fn": 0}
    assert result["section_10_acceptance_status"] == "unavailable_final_dataset"
    assert (
        result["current_scope_metrics"]["volume_error"]
        ["median_absolute_percentage_error"]
        == pytest.approx(123.31547582373172)
    )
    assert result["current_scope_metrics"]["theft_rule_recall"]["trials"] == 2
    assert result["current_scope_metrics"]["false_positive_rate"]["trials"] == 8
    assert result["alert_confusion_matrix"] == {
        "ALERT": {"ALERT": 2},
        "NO_ALERT": {"NO_ALERT": 8},
    }


def test_gate6_evaluation_is_deterministic() -> None:
    assert evaluate_split(SPLIT_ROOT) == evaluate_split(SPLIT_ROOT)


def test_gate6_loader_rejects_missing_fixture(tmp_path: Path) -> None:
    with pytest.raises(Gate6EvaluationError, match="does not exist"):
        load_gate6_split(tmp_path / "missing")


def test_gate6_loader_rejects_checksum_mismatch(tmp_path: Path) -> None:
    destination = tmp_path / "gate6"
    shutil.copytree(SPLIT_ROOT, destination)
    checksum_path = destination / "checksums.sha256"
    lines = checksum_path.read_text(encoding="utf-8").splitlines()
    lines[0] = "0" * 64 + lines[0][64:]
    checksum_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    with pytest.raises(Gate6EvaluationError, match="checksum inventory"):
        load_gate6_split(destination)


def test_gate6_loader_rejects_malformed_index(tmp_path: Path) -> None:
    destination = tmp_path / "gate6"
    shutil.copytree(SPLIT_ROOT, destination)
    index_path = destination / "gate6.json"
    index = json.loads(index_path.read_text(encoding="utf-8"))
    index["scenarios"] = []
    index_path.write_text(json.dumps(index), encoding="utf-8")

    with pytest.raises(Gate6EvaluationError, match="must contain scenarios"):
        load_gate6_split(destination)


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("baseline_frame_count", 29, "30 baseline"),
        ("minimum_event_frame_count", 6, "7 event"),
        ("frame_interval_ns", 50_000_000, "100 ms"),
    ],
)
def test_gate6_loader_rejects_inconsistent_split_metadata(
    tmp_path: Path,
    field: str,
    value: int,
    message: str,
) -> None:
    destination = tmp_path / "gate6"
    shutil.copytree(SPLIT_ROOT, destination)
    index_path = destination / "gate6.json"
    index = json.loads(index_path.read_text(encoding="utf-8"))
    index[field] = value
    index_path.write_text(json.dumps(index), encoding="utf-8")
    _refresh_checksums(destination)

    with pytest.raises(Gate6EvaluationError, match=message):
        load_gate6_split(destination)


def test_gate6_loader_rejects_manifest_frame_count_and_spacing(tmp_path: Path) -> None:
    destination = tmp_path / "gate6"
    shutil.copytree(SPLIT_ROOT, destination)
    manifest_path = destination / "addition" / "scenario.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["baseline_frame_ids"].pop()
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    _refresh_checksums(destination)

    with pytest.raises(Gate6EvaluationError, match="exactly 30 baseline"):
        load_gate6_split(destination)

    shutil.copytree(SPLIT_ROOT, destination / "spacing-copy")
    spacing_root = destination / "spacing-copy"
    spacing_manifest_path = spacing_root / "addition" / "scenario.json"
    spacing_manifest = json.loads(spacing_manifest_path.read_text(encoding="utf-8"))
    spacing_manifest["frames"][1]["timestamp_ns"] += 1
    spacing_manifest_path.write_text(json.dumps(spacing_manifest), encoding="utf-8")
    _refresh_checksums(spacing_root)

    with pytest.raises(Gate6EvaluationError, match="100 ms"):
        load_gate6_split(spacing_root)


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("scenario_id", "wrong-id", "scenario ID mismatch"),
        ("seed", 9999, "seed mismatch"),
        ("expected_event_types", ["ADDITION"], "expected event metadata mismatch"),
        ("expected_alert", False, "expected alert metadata mismatch"),
    ],
)
def test_gate6_loader_cross_validates_index_metadata(
    tmp_path: Path,
    field: str,
    value: object,
    message: str,
) -> None:
    destination = tmp_path / "gate6"
    shutil.copytree(SPLIT_ROOT, destination)
    index_path = destination / "gate6.json"
    index = json.loads(index_path.read_text(encoding="utf-8"))
    index["scenarios"][0][field] = value
    index_path.write_text(json.dumps(index), encoding="utf-8")
    _refresh_checksums(destination)

    with pytest.raises(Gate6EvaluationError, match=message):
        load_gate6_split(destination)


def test_event_scoring_requires_matching_change_type() -> None:
    row, counts, _, _ = _score_scenario(
        _manifest(ChangeType.REMOVAL),
        _result(ChangeType.ADDITION.value),
        _entry(),
        EvaluationConfig(),
    )

    assert counts == {"tp": 0, "fp": 1, "fn": 1}
    assert row["event_pass"] is False


@pytest.mark.parametrize(
    ("expected", "actual", "counts"),
    [
        (ChangeType.REMOVAL, None, {"tp": 0, "fp": 0, "fn": 1}),
        (None, ChangeType.ADDITION.value, {"tp": 0, "fp": 1, "fn": 0}),
        (ChangeType.REMOVAL, ChangeType.REMOVAL.value, {"tp": 1, "fp": 0, "fn": 0}),
    ],
)
def test_event_scoring_covers_fn_fp_and_tp(
    expected: ChangeType | None,
    actual: str | None,
    counts: dict[str, int],
) -> None:
    _, actual_counts, _, _ = _score_scenario(
        _manifest(expected),
        _result(actual),
        _entry(),
        EvaluationConfig(),
    )
    assert actual_counts == counts


def test_alert_scoring_covers_false_positive_and_false_negative() -> None:
    _, _, _, false_positive = _score_scenario(
        _manifest(ChangeType.REMOVAL, should_alert=False),
        _result(ChangeType.REMOVAL.value, alert=True),
        _entry(),
        EvaluationConfig(),
    )
    _, _, _, false_negative = _score_scenario(
        _manifest(ChangeType.REMOVAL, should_alert=True),
        _result(ChangeType.REMOVAL.value, alert=False),
        _entry(),
        EvaluationConfig(),
    )
    assert false_positive == {"tp": 0, "fp": 1, "fn": 0}
    assert false_negative == {"tp": 0, "fp": 0, "fn": 1}


def test_non_perfect_classification_formulas() -> None:
    metrics = _classification({"tp": 1, "fp": 1, "fn": 2})

    assert metrics["precision"] == 0.5
    assert metrics["recall"] == pytest.approx(1 / 3)
    assert metrics["f1"] == pytest.approx(0.4)


def test_binomial_confidence_interval_is_reproducible() -> None:
    result = evaluate_split(SPLIT_ROOT)

    interval = result["current_scope_metrics"]["theft_rule_recall"]
    assert interval["point"] == 1.0
    assert interval["lower"] < interval["point"] <= interval["upper"]


def test_timing_volume_and_bounds_metrics() -> None:
    row, _, _, _ = _score_scenario(
        _manifest(ChangeType.REMOVAL),
        _result(
            ChangeType.REMOVAL.value,
            first_seen_timestamp_ns=150,
            volume_m3=1.5,
            bounds_min_m=(0.5, 0.5, 0.5),
            bounds_max_m=(1.5, 1.5, 1.5),
        ),
        _entry(),
        EvaluationConfig(),
    )

    assert row["detection_timing_ns"] == 50
    assert row["volume_relative_error"] == 0.25
    assert row["bounds_iou"] == pytest.approx(1 / 15)


def test_gate6_threshold_configuration_is_explicit() -> None:
    pending = evaluate_split(SPLIT_ROOT)
    configured = evaluate_split(
        SPLIT_ROOT,
        config=EvaluationConfig(
            timing_tolerance_ns=3_000_000_000,
            volume_error_threshold=10.0,
            bounds_iou_threshold=0.0,
        ),
    )

    partial = evaluate_split(
        SPLIT_ROOT,
        config=EvaluationConfig(timing_tolerance_ns=3_000_000_000),
    )

    assert pending["acceptance_status"] == "pending"
    assert pending["threshold_status"]["overall"] == "no_thresholds_configured"
    assert partial["acceptance_status"] == "pending"
    assert partial["threshold_status"]["overall"] == "partially_configured"
    assert configured["acceptance_status"] == "passed"
    assert configured["threshold_status"]["overall"] == "all_thresholds_passed"
    assert all(
        configured["threshold_status"][name] == "configured"
        for name in ("timing", "volume", "bounds")
    )


from kyra.evaluation.comparison import get_paradigm_comparisons
from kyra.evaluation.dataset import (
    HELD_OUT_CATEGORIES,
    generate_evaluation_specs,
)
from kyra.evaluation.metrics import (
    ScenarioEvaluationResult,
    calculate_suite_metrics,
    wilson_score_interval,
)
from kyra.evaluation.runner import evaluate_scenario_spec


def test_wilson_score_interval_bounds() -> None:
    low, high = wilson_score_interval(0, 100)
    assert low == 0.0
    assert 0.0 < high < 0.05

    low, high = wilson_score_interval(100, 100)
    assert 0.95 < low < 1.0
    assert high == 1.0

    low, high = wilson_score_interval(50, 100)
    assert 0.39 < low < 0.42
    assert 0.58 < high < 0.61

    import pytest
    with pytest.raises(ValueError):
        wilson_score_interval(10, 5)


def test_dataset_spec_counts_and_splits() -> None:
    specs = generate_evaluation_specs()
    assert len(specs) == 420

    positives = [s for s in specs if s.is_positive]
    negatives = [s for s in specs if not s.is_positive]

    assert len(positives) == 120
    assert len(negatives) == 300

    total_categories = sum(len(cats) for cats in HELD_OUT_CATEGORIES.values())
    assert total_categories == 20

    procedural = [s for s in positives if "reversed-ocid" not in s.scenario_id]
    reversed_ocid = [s for s in positives if "reversed-ocid" in s.scenario_id]
    assert len(procedural) == 60
    assert len(reversed_ocid) == 60


def test_calculate_suite_metrics() -> None:
    results = [
        ScenarioEvaluationResult(
            scenario_id=f"pos-{i}",
            is_positive=True,
            expected_change_type="removal",
            actual_change_type="removal",
            expected_alert=True,
            actual_alert=True,
            expected_volume_m3=0.001,
            actual_volume_m3=0.00105,
            latency_ms=50.0,
        )
        for i in range(10)
    ] + [
        ScenarioEvaluationResult(
            scenario_id=f"neg-{i}",
            is_positive=False,
            expected_change_type=None,
            actual_change_type=None,
            expected_alert=False,
            actual_alert=False,
            latency_ms=45.0,
        )
        for i in range(20)
    ]

    metrics = calculate_suite_metrics(results)
    assert metrics["theft_rule_recall"] == 1.0
    assert metrics["recall_passed"] is True
    assert metrics["false_positive_rate"] == 0.0
    assert metrics["fpr_passed"] is True
    assert metrics["geometry_balanced_accuracy"] == 1.0
    assert metrics["geometry_accuracy_passed"] is True
    assert metrics["volume_mape"] <= 0.10
    assert metrics["volume_mape_passed"] is True


def test_evaluate_sample_spec() -> None:
    specs = generate_evaluation_specs()
    pos_res = evaluate_scenario_spec(specs[0])
    assert pos_res.is_positive is True
    assert pos_res.actual_alert is True
    assert pos_res.actual_change_type == "removal"

    neg_res = evaluate_scenario_spec(specs[120])
    assert neg_res.is_positive is False
    assert neg_res.actual_alert is False


def test_paradigm_comparisons() -> None:
    comparisons = get_paradigm_comparisons()
    assert len(comparisons) == 6
    dims = [c.dimension for c in comparisons]
    assert "Per-SKU Annotation & Retraining" in dims
    assert "Held-out Category Generalization (20 Categories)" in dims

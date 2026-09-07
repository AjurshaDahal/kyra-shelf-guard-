"""Unit tests for Gate 6 evaluation framework."""

from __future__ import annotations

import pytest

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
    # 0 out of 100
    low, high = wilson_score_interval(0, 100)
    assert low == 0.0
    assert 0.0 < high < 0.05

    # 100 out of 100
    low, high = wilson_score_interval(100, 100)
    assert 0.95 < low < 1.0
    assert high == 1.0

    # 50 out of 100: should be centered around 0.5
    low, high = wilson_score_interval(50, 100)
    assert 0.39 < low < 0.42
    assert 0.58 < high < 0.61

    # Invalid input checks
    with pytest.raises(ValueError):
        wilson_score_interval(10, 5)


def test_dataset_spec_counts_and_splits() -> None:
    specs = generate_evaluation_specs()
    assert len(specs) == 420

    positives = [s for s in specs if s.is_positive]
    negatives = [s for s in specs if not s.is_positive]

    assert len(positives) == 120
    assert len(negatives) == 300

    # Verify 20 held-out categories
    total_categories = sum(len(cats) for cats in HELD_OUT_CATEGORIES.values())
    assert total_categories == 20

    # 60 procedural (20 * 3) + 60 reversed transitions
    procedural = [s for s in positives if "reversed-ocid" not in s.scenario_id]
    reversed_ocid = [s for s in positives if "reversed-ocid" in s.scenario_id]
    assert len(procedural) == 60
    assert len(reversed_ocid) == 60


def test_calculate_suite_metrics() -> None:
    # Synthetic results mock
    results = [
        # 10 positives, all alerted
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
        # 20 negatives, none alerted
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
    # Test first positive
    pos_res = evaluate_scenario_spec(specs[0])
    assert pos_res.is_positive is True
    assert pos_res.actual_alert is True
    assert pos_res.actual_change_type == "removal"

    # Test first negative (occlusion-only)
    neg_res = evaluate_scenario_spec(specs[120])
    assert neg_res.is_positive is False
    assert neg_res.actual_alert is False


def test_paradigm_comparisons() -> None:
    comparisons = get_paradigm_comparisons()
    assert len(comparisons) == 6
    dims = [c.dimension for c in comparisons]
    assert "Per-SKU Annotation & Retraining" in dims
    assert "Held-out Category Generalization (20 Categories)" in dims

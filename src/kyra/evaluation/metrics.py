"""Evaluation metrics and confidence interval computation for Gate 6."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any


def wilson_score_interval(
    successes: int,
    total: int,
    confidence: float = 0.95,
) -> tuple[float, float]:
    """Compute Wilson score binomial confidence interval.

    Args:
        successes: Number of positive outcomes (e.g. true alerts).
        total: Total number of trials.
        confidence: Confidence level (default 0.95 for 95% CI).

    Returns:
        tuple of (lower_bound, upper_bound) as floats between 0.0 and 1.0.
    """
    if total <= 0:
        return 0.0, 0.0
    if successes < 0 or successes > total:
        raise ValueError("successes must be between 0 and total")

    if abs(confidence - 0.95) < 1e-3:
        z = 1.959963984540054
    elif abs(confidence - 0.99) < 1e-3:
        z = 2.5758293035489004
    else:
        z = 1.96

    p = successes / total
    denominator = 1.0 + (z * z) / total
    centre = (p + (z * z) / (2.0 * total)) / denominator
    half_width = (z / denominator) * math.sqrt(
        (p * (1.0 - p) / total) + (z * z) / (4.0 * total * total)
    )

    lower = 0.0 if successes == 0 else max(0.0, centre - half_width)
    upper = 1.0 if successes == total else min(1.0, centre + half_width)
    return lower, upper


@dataclass
class ScenarioEvaluationResult:
    scenario_id: str
    is_positive: bool
    expected_change_type: str | None
    actual_change_type: str | None
    expected_alert: bool
    actual_alert: bool
    expected_volume_m3: float | None = None
    actual_volume_m3: float | None = None
    latency_ms: float = 0.0


def calculate_suite_metrics(results: list[ScenarioEvaluationResult]) -> dict[str, Any]:
    """Calculate Gate 6 metrics across evaluation trial results."""
    positives = [r for r in results if r.is_positive]
    negatives = [r for r in results if not r.is_positive]

    total_positive = len(positives)
    total_negative = len(negatives)

    true_alerts = sum(1 for r in positives if r.expected_alert and r.actual_alert)
    expected_positive_alerts = sum(1 for r in positives if r.expected_alert)
    recall = true_alerts / expected_positive_alerts if expected_positive_alerts > 0 else 0.0
    recall_ci_low, recall_ci_high = wilson_score_interval(true_alerts, expected_positive_alerts)

    false_alerts = sum(1 for r in negatives if r.actual_alert)
    fpr = false_alerts / total_negative if total_negative > 0 else 0.0
    fpr_ci_low, fpr_ci_high = wilson_score_interval(false_alerts, total_negative)

    geom_pos_correct = sum(
        1
        for r in positives
        if r.expected_change_type is not None and r.actual_change_type == r.expected_change_type
    )
    geom_tpr = geom_pos_correct / total_positive if total_positive > 0 else 0.0

    geom_neg_correct = sum(
        1
        for r in negatives
        if r.actual_change_type in (None, "unknown", "no_change", r.expected_change_type)
        and r.actual_change_type != "removal"
    )
    geom_tnr = geom_neg_correct / total_negative if total_negative > 0 else 0.0
    balanced_accuracy = (geom_tpr + geom_tnr) / 2.0

    volume_errors: list[float] = []
    for r in positives:
        if (
            r.expected_volume_m3 is not None
            and r.actual_volume_m3 is not None
            and r.expected_volume_m3 >= 0.0005
            and r.actual_volume_m3 > 0.0
        ):
            ape = abs(r.actual_volume_m3 - r.expected_volume_m3) / r.expected_volume_m3
            volume_errors.append(ape)

    volume_mape = float(sorted(volume_errors)[len(volume_errors) // 2]) if volume_errors else 0.0

    latencies = [r.latency_ms for r in results]
    latencies_sorted = sorted(latencies)
    p50_ms = latencies_sorted[int(len(latencies_sorted) * 0.50)] if latencies else 0.0
    p95_ms = latencies_sorted[int(len(latencies_sorted) * 0.95)] if latencies else 0.0
    avg_fps = (
        (1000.0 / (sum(latencies) / len(latencies))) if latencies and sum(latencies) > 0 else 0.0
    )

    return {
        "total_trials": len(results),
        "total_positive": total_positive,
        "total_negative": total_negative,
        "true_alerts": true_alerts,
        "expected_alerts": expected_positive_alerts,
        "false_alerts": false_alerts,
        "theft_rule_recall": recall,
        "theft_rule_recall_95ci": (recall_ci_low, recall_ci_high),
        "recall_passed": recall >= 0.92,
        "false_positive_rate": fpr,
        "false_positive_rate_95ci": (fpr_ci_low, fpr_ci_high),
        "fpr_passed": fpr <= 0.011,
        "geometry_balanced_accuracy": balanced_accuracy,
        "geometry_accuracy_passed": balanced_accuracy >= 0.90,
        "volume_mape": volume_mape,
        "volume_mape_passed": volume_mape <= 0.10,
        "latency_p50_ms": p50_ms,
        "latency_p95_ms": p95_ms,
        "throughput_fps": avg_fps,
    }

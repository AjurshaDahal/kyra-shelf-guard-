"""Evaluation and benchmarking framework for Kyra."""

from kyra.evaluation.comparison import (
    ParadigmComparisonDimension,
    evaluate_class_based_baseline_summary,
    get_paradigm_comparisons,
)
from kyra.evaluation.dataset import (
    HELD_OUT_CATEGORIES,
    EvaluationScenarioSpec,
    generate_evaluation_specs,
    materialize_scenario,
)
from kyra.evaluation.metrics import (
    ScenarioEvaluationResult,
    calculate_suite_metrics,
    wilson_score_interval,
)
from kyra.evaluation.runner import evaluate_scenario_spec, run_evaluation_suite

__all__ = [
    "HELD_OUT_CATEGORIES",
    "EvaluationScenarioSpec",
    "ParadigmComparisonDimension",
    "ScenarioEvaluationResult",
    "calculate_suite_metrics",
    "evaluate_class_based_baseline_summary",
    "evaluate_scenario_spec",
    "generate_evaluation_specs",
    "get_paradigm_comparisons",
    "materialize_scenario",
    "run_evaluation_suite",
    "wilson_score_interval",
]

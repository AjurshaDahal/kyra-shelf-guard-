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
from kyra.evaluation.gate6 import (
    EvaluationConfig,
    Gate6EvaluationError,
    evaluate_split,
    load_gate6_split,
)
from kyra.evaluation.metrics import (
    ScenarioEvaluationResult,
    calculate_suite_metrics,
    wilson_score_interval,
)
from kyra.evaluation.runner import evaluate_scenario_spec, run_evaluation_suite

__all__ = [
    "EvaluationConfig",
    "EvaluationScenarioSpec",
    "Gate6EvaluationError",
    "HELD_OUT_CATEGORIES",
    "ParadigmComparisonDimension",
    "ScenarioEvaluationResult",
    "calculate_suite_metrics",
    "evaluate_class_based_baseline_summary",
    "evaluate_scenario_spec",
    "evaluate_split",
    "generate_evaluation_specs",
    "get_paradigm_comparisons",
    "load_gate6_split",
    "materialize_scenario",
    "run_evaluation_suite",
    "wilson_score_interval",
]

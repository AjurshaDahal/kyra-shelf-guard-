"""Evaluation runner for executing Gate 6 test suites."""

from __future__ import annotations

import shutil
import tempfile
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any

from kyra.evaluation.dataset import EvaluationScenarioSpec, materialize_scenario
from kyra.evaluation.metrics import ScenarioEvaluationResult, calculate_suite_metrics
from kyra.manifest import load_manifest
from kyra.pipeline import run_scenario


def evaluate_scenario_spec(
    spec: EvaluationScenarioSpec,
    work_dir: Path | None = None,
) -> ScenarioEvaluationResult:
    """Materialize and evaluate a single scenario specification."""
    is_temp = work_dir is None
    target_dir = (
        Path(tempfile.mkdtemp(prefix=f"eval_{spec.scenario_id}_"))
        if is_temp
        else work_dir / spec.scenario_id
    )
    target_dir.mkdir(parents=True, exist_ok=True)

    try:
        manifest_path = materialize_scenario(spec, target_dir)
        manifest = load_manifest(manifest_path)

        t0 = time.perf_counter()
        pipeline_result = run_scenario(manifest_path)
        elapsed_ms = (time.perf_counter() - t0) * 1000.0

        expected_change = spec.change_type.value.lower() if spec.change_type is not None else None
        actual_change = (
            pipeline_result["events"][0]["change_type"].lower()
            if pipeline_result["events"]
            else None
        )

        actual_alert = int(pipeline_result.get("alert_count", 0)) > 0

        # Volume ground truth and estimate
        expected_vol = (
            manifest.ground_truth_events[0].volume_m3 if manifest.ground_truth_events else None
        )
        actual_vol = (
            pipeline_result["events"][0]["volume_m3"]
            if pipeline_result["events"] and "volume_m3" in pipeline_result["events"][0]
            else None
        )

        return ScenarioEvaluationResult(
            scenario_id=spec.scenario_id,
            is_positive=spec.is_positive,
            expected_change_type=expected_change,
            actual_change_type=actual_change,
            expected_alert=spec.should_alert,
            actual_alert=actual_alert,
            expected_volume_m3=expected_vol,
            actual_volume_m3=actual_vol,
            latency_ms=elapsed_ms,
        )
    finally:
        if is_temp and target_dir.exists():
            shutil.rmtree(target_dir, ignore_errors=True)


def run_evaluation_suite(
    specs: list[EvaluationScenarioSpec],
    progress_callback: Callable[[int, int, str], None] | None = None,
    work_dir: Path | None = None,
) -> dict[str, Any]:
    """Execute evaluation over a list of scenario specifications."""
    results: list[ScenarioEvaluationResult] = []
    total = len(specs)

    for idx, spec in enumerate(specs):
        result = evaluate_scenario_spec(spec, work_dir=work_dir)
        results.append(result)
        if progress_callback is not None:
            progress_callback(idx + 1, total, spec.scenario_id)

    metrics = calculate_suite_metrics(results)
    return {
        "metrics": metrics,
        "results": results,
    }

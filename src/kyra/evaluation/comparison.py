"""Class-based YOLO comparison framework for Gate 6 (Section 11)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ParadigmComparisonDimension:
    dimension: str
    class_based_yolo: str
    kyra_physics_geometry: str
    advantage: str


def get_paradigm_comparisons() -> list[ParadigmComparisonDimension]:
    """Return structured comparisons across the 6 dimensions defined in Section 11."""
    return [
        ParadigmComparisonDimension(
            dimension="Per-SKU Annotation & Retraining",
            class_based_yolo=(
                "A SKU classifier generally needs labelled examples for categories it is expected "
                "to recognize; the amount of data and retraining depends on the deployment."
            ),
            kyra_physics_geometry=(
                "The implemented geometry path does not classify shelf items and does not consume "
                "SKU-specific training data."
            ),
            advantage="Design-level difference; no operational cost comparison was measured.",
        ),
        ParadigmComparisonDimension(
            dimension="Held-out Category Generalization (20 Categories)",
            class_based_yolo=(
                "An off-the-shelf classifier may not name categories outside its label set. No "
                "class-based baseline was executed in this project."
            ),
            kyra_physics_geometry=(
                "The generated fixture matrix uses 20 category names, but the shapes are "
                "procedural "
                "and do not establish real unseen-category accuracy."
            ),
            advantage="Hypothesis to test on independently sourced recordings.",
        ),
        ParadigmComparisonDimension(
            dimension="Compute and Calibration Requirements",
            class_based_yolo=(
                "Compute and calibration requirements depend on the selected detector and camera "
                "pipeline; they were not benchmarked here."
            ),
            kyra_physics_geometry=(
                "The deterministic geometry core runs on CPU and uses metric calibration; optional "
                "MiDaS and YOLO inference have separate compute requirements."
            ),
            advantage="Kyra exposes an auditable metric-geometry core.",
        ),
        ParadigmComparisonDimension(
            dimension="Irregular and Thin-Item Failure Modes",
            class_based_yolo=(
                "Dense, thin, and irregular shelf items are plausible classifier failure modes, "
                "but this project did not measure a 2D baseline on them."
            ),
            kyra_physics_geometry=(
                "Signed depth differencing detects the generated thin and irregular fixtures; real "
                "shelf-removal recordings are still required to measure generalization."
            ),
            advantage="Potential geometry advantage; real-data comparison pending.",
        ),
        ParadigmComparisonDimension(
            dimension="Occlusion Sensitivity",
            class_based_yolo=(
                "Occlusion can affect both 2D detection and depth observation; no comparative "
                "occlusion benchmark was run."
            ),
            kyra_physics_geometry=(
                "Explicit occlusion ratio tracking: confirms events only after occlusion "
                "clears and requires temporal persistence (>=5 of 7 observations)."
            ),
            advantage="Kyra has explicit fail-closed occlusion handling in tested fixtures.",
        ),
        ParadigmComparisonDimension(
            dimension="Inferential Boundary & Legal Positioning",
            class_based_yolo=(
                "An item classifier identifies visual categories; by itself it does not establish "
                "intent."
            ),
            kyra_physics_geometry=(
                "Strictly reports 'suspicious shelf-removal alert' based on physical volume loss "
                "paired with temporal person proximity. Does not claim theft proof."
            ),
            advantage="Kyra documents a human-review boundary.",
        ),
    ]


def evaluate_class_based_baseline_summary() -> dict[str, Any]:
    """Return a design comparison without presenting unrun baseline metrics."""
    comparisons = get_paradigm_comparisons()
    return {
        "dimensions_evaluated": len(comparisons),
        "comparisons": [
            {
                "dimension": c.dimension,
                "yolo_behavior": c.class_based_yolo,
                "kyra_behavior": c.kyra_physics_geometry,
                "advantage": c.advantage,
            }
            for c in comparisons
        ],
        "comparison_kind": "design-only; no class-based accuracy baseline executed",
        "summary": (
            "Kyra's implemented geometry path does not require SKU labels. Comparative accuracy, "
            "retraining cost, and real unseen-category generalization remain unmeasured."
        ),
    }

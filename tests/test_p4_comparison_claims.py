from __future__ import annotations

from kyra.evaluation.comparison import get_paradigm_comparisons


def test_paradigm_comparison_does_not_claim_unrun_accuracy() -> None:
    rendered = " ".join(
        field
        for comparison in get_paradigm_comparisons()
        for field in (
            comparison.class_based_yolo,
            comparison.kyra_physics_geometry,
            comparison.advantage,
        )
    )

    assert "Recall ~ 0-15%" not in rendered
    assert "achieves >90%" not in rendered
    assert "No class-based baseline was executed" in rendered

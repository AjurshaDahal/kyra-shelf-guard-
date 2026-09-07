"""Person 2 occlusion subpackage: shelf visibility and occlusion safety."""

from kyra.occlusion.safety import (
    OcclusionSafetyResult,
    evaluate_occlusion_safety,
)

__all__ = [
    "OcclusionSafetyResult",
    "evaluate_occlusion_safety",
]

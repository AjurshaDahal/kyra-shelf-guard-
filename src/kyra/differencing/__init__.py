"""Person 2 differencing subpackage: signed depth difference and noise thresholding."""

from kyra.differencing.signed_diff import (
    SignedDifferenceResult,
    compute_signed_depth_difference,
)

__all__ = [
    "SignedDifferenceResult",
    "compute_signed_depth_difference",
]

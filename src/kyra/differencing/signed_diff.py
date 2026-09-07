"""Signed depth differencing with noise-adaptive thresholding for Person 2."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from kyra.contracts import BaselineArtifact, ShelfConfig


@dataclass(slots=True, frozen=True)
class SignedDifferenceResult:
    """Result of signed depth differencing over shelf region."""

    delta_z_m: np.ndarray
    threshold_m: np.ndarray
    removal_candidate_mask: np.ndarray
    addition_candidate_mask: np.ndarray
    unknown_mask: np.ndarray
    no_change_mask: np.ndarray
    valid_count: int
    removal_pixel_count: int
    addition_pixel_count: int
    unknown_pixel_count: int


def compute_signed_depth_difference(
    current_depth_m: np.ndarray,
    baseline: BaselineArtifact,
    shelf_config: ShelfConfig,
    valid_depth_mask: np.ndarray,
    *,
    person_occlusion_mask: np.ndarray | None = None,
) -> SignedDifferenceResult:
    """Compute signed depth differencing against opening baseline.

    Applies the M3C2-EP error propagation model:
        threshold(u, v) = max(removal_floor_m, 3 * noise_sigma(u, v))

    Classifications:
        - Farther valid surface (Δz > threshold) -> candidate REMOVAL
        - Nearer valid surface (Δz < -threshold) -> candidate ADDITION
        - Invalid / missing / occluded depth -> UNKNOWN (never free space)
        - Small delta (|Δz| <= threshold) -> NO_CHANGE

    Args:
        current_depth_m: 2D float32 depth map (metres), ideally drift-corrected.
        baseline: BaselineArtifact containing baseline depth and noise sigma.
        shelf_config: Shelf configuration including ROI and removal floor.
        valid_depth_mask: 2D boolean mask of valid depth pixels in current frame.
        person_occlusion_mask: Optional 2D boolean mask of person occlusions.

    Returns:
        SignedDifferenceResult with signed deltas and boolean classification masks.
    """
    h, w = current_depth_m.shape
    x1, y1, x2, y2 = shelf_config.roi_xyxy

    roi_mask = np.zeros((h, w), dtype=bool)
    roi_mask[max(0, y1) : min(h, y2), max(0, x1) : min(w, x2)] = True

    # Identify invalid depth
    invalid_current = (
        ~valid_depth_mask | ~np.isfinite(current_depth_m) | (current_depth_m <= 0)
    )
    invalid_baseline = (
        ~baseline.valid_mask
        | ~np.isfinite(baseline.baseline_depth_m)
        | (baseline.baseline_depth_m <= 0)
    )
    person_blocked = (
        np.zeros((h, w), dtype=bool)
        if person_occlusion_mask is None
        else person_occlusion_mask.astype(bool)
    )

    # Unknown region: invalid in current, invalid in baseline, or occluded by person
    unknown_mask = roi_mask & (invalid_current | invalid_baseline | person_blocked)

    # Valid evaluation region within ROI
    valid_eval = roi_mask & ~unknown_mask

    # Signed difference: Δz = z_curr - z_base
    delta_z = np.zeros((h, w), dtype=np.float32)
    delta_z[valid_eval] = current_depth_m[valid_eval] - baseline.baseline_depth_m[valid_eval]

    # Per-pixel adaptive threshold: max(removal_floor_m, 3 * noise_sigma_m)
    threshold_m = np.maximum(
        shelf_config.removal_floor_m,
        3.0 * baseline.noise_sigma_m,
    ).astype(np.float32)

    # Candidate masks
    removal_mask = valid_eval & (delta_z > threshold_m)
    addition_mask = valid_eval & (delta_z < -threshold_m)
    no_change_mask = valid_eval & ~removal_mask & ~addition_mask

    return SignedDifferenceResult(
        delta_z_m=delta_z,
        threshold_m=threshold_m,
        removal_candidate_mask=removal_mask,
        addition_candidate_mask=addition_mask,
        unknown_mask=unknown_mask,
        no_change_mask=no_change_mask,
        valid_count=int(np.count_nonzero(valid_eval)),
        removal_pixel_count=int(np.count_nonzero(removal_mask)),
        addition_pixel_count=int(np.count_nonzero(addition_mask)),
        unknown_pixel_count=int(np.count_nonzero(unknown_mask)),
    )

from __future__ import annotations

import numpy as np

from kyra.contracts import BaselineArtifact, ShelfConfig
from kyra.differencing.signed_diff import compute_signed_depth_difference


def _make_baseline(width: int = 32, height: int = 24) -> BaselineArtifact:
    depth = np.full((height, width), 1.0, dtype=np.float32)
    valid = np.ones((height, width), dtype=bool)
    fixed = np.ones((height, width), dtype=bool)
    noise = np.full((height, width), 0.002, dtype=np.float32)
    occupancy = np.zeros((height, width, 1), dtype=np.uint8)

    return BaselineArtifact(
        shelf_id="shelf-diff-01",
        roi_xyxy=(4, 4, 28, 20),
        bounds_min_m=(-0.5, -0.5, 0.4),
        bounds_max_m=(0.5, 0.5, 1.8),
        baseline_depth_m=depth,
        valid_mask=valid,
        fixed_geometry_mask=fixed,
        portable_components=(),
        occupancy_grid=occupancy,
        noise_sigma_m=noise,
        intrinsics=np.eye(3, dtype=np.float64),
        camera_to_shelf=np.eye(4, dtype=np.float64),
        calibration_checksum="b" * 64,
    )


def _make_shelf_config() -> ShelfConfig:
    return ShelfConfig(
        shelf_id="shelf-diff-01",
        roi_xyxy=(4, 4, 28, 20),
        bounds_min_m=(-0.5, -0.5, 0.4),
        bounds_max_m=(0.5, 0.5, 1.8),
        removal_floor_m=0.015,
    )


def test_signed_depth_difference_removal() -> None:
    baseline = _make_baseline()
    config = _make_shelf_config()

    current_depth = baseline.baseline_depth_m.copy()
    valid_mask = baseline.valid_mask.copy()

    # Create a 4x4 removal region where surface is farther by 30 mm
    current_depth[10:14, 10:14] += 0.030

    result = compute_signed_depth_difference(current_depth, baseline, config, valid_mask)
    assert result.removal_pixel_count == 16
    assert result.addition_pixel_count == 0
    assert np.all(result.removal_candidate_mask[10:14, 10:14])
    assert not np.any(result.addition_candidate_mask)


def test_signed_depth_difference_addition() -> None:
    baseline = _make_baseline()
    config = _make_shelf_config()

    current_depth = baseline.baseline_depth_m.copy()
    valid_mask = baseline.valid_mask.copy()

    # Create a 4x4 addition region where surface is nearer by 30 mm
    current_depth[10:14, 10:14] -= 0.030

    result = compute_signed_depth_difference(current_depth, baseline, config, valid_mask)
    assert result.removal_pixel_count == 0
    assert result.addition_pixel_count == 16
    assert np.all(result.addition_candidate_mask[10:14, 10:14])
    assert not np.any(result.removal_candidate_mask)


def test_signed_depth_difference_no_change() -> None:
    baseline = _make_baseline()
    config = _make_shelf_config()

    current_depth = baseline.baseline_depth_m.copy()
    valid_mask = baseline.valid_mask.copy()

    # Tiny depth perturbation below 15 mm floor (5 mm)
    current_depth[10:14, 10:14] += 0.005

    result = compute_signed_depth_difference(current_depth, baseline, config, valid_mask)
    assert result.removal_pixel_count == 0
    assert result.addition_pixel_count == 0
    assert np.all(result.no_change_mask[10:14, 10:14])


def test_signed_depth_difference_noise_adaptive_threshold() -> None:
    baseline = _make_baseline()
    config = _make_shelf_config()

    # Set high noise on patch: sigma = 0.010 m -> 3*sigma = 0.030 m
    baseline.noise_sigma_m[10:14, 10:14] = 0.010

    current_depth = baseline.baseline_depth_m.copy()
    valid_mask = baseline.valid_mask.copy()

    # Change of 20 mm exceeds removal_floor (15 mm) but is below 3*sigma (30 mm)
    current_depth[10:14, 10:14] += 0.020

    result = compute_signed_depth_difference(current_depth, baseline, config, valid_mask)
    # Must be suppressed by M3C2-EP noise model
    assert result.removal_pixel_count == 0
    assert np.all(result.no_change_mask[10:14, 10:14])


def test_signed_depth_difference_unknown_invariants() -> None:
    baseline = _make_baseline()
    config = _make_shelf_config()

    current_depth = baseline.baseline_depth_m.copy()
    valid_mask = baseline.valid_mask.copy()

    # Set various invalid conditions
    current_depth[6, 6] = 0.0          # Zero depth
    current_depth[7, 7] = np.nan       # NaN depth
    valid_mask[8, 8] = False           # Masked invalid

    person_mask = np.zeros_like(valid_mask)
    person_mask[10:12, 10:12] = True   # Person occluded

    result = compute_signed_depth_difference(
        current_depth, baseline, config, valid_mask, person_occlusion_mask=person_mask
    )

    assert result.unknown_mask[6, 6]
    assert result.unknown_mask[7, 7]
    assert result.unknown_mask[8, 8]
    assert np.all(result.unknown_mask[10:12, 10:12])

    # Invariants: Unknown pixels must NEVER be candidate removals
    assert not result.removal_candidate_mask[6, 6]
    assert not result.removal_candidate_mask[7, 7]
    assert not result.removal_candidate_mask[8, 8]
    assert not np.any(result.removal_candidate_mask[10:12, 10:12])

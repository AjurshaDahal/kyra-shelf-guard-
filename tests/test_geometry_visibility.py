from __future__ import annotations

import numpy as np
import pytest

from kyra.contracts import BaselineArtifact, FramePacket, ShelfConfig, SourceType
from kyra.occlusion.safety import evaluate_occlusion_safety


def _make_baseline(width: int = 32, height: int = 24) -> BaselineArtifact:
    depth = np.full((height, width), 1.0, dtype=np.float32)
    valid = np.ones((height, width), dtype=bool)
    occupancy = np.zeros((height, width, 1), dtype=np.uint8)

    return BaselineArtifact(
        shelf_id="shelf-occ-01",
        roi_xyxy=(0, 0, width, height),
        bounds_min_m=(-0.5, -0.5, 0.4),
        bounds_max_m=(0.5, 0.5, 1.8),
        baseline_depth_m=depth,
        valid_mask=valid,
        fixed_geometry_mask=valid.copy(),
        portable_components=(),
        occupancy_grid=occupancy,
        noise_sigma_m=np.zeros((height, width), dtype=np.float32),
        intrinsics=np.eye(3, dtype=np.float64),
        camera_to_shelf=np.eye(4, dtype=np.float64),
        calibration_checksum="c" * 64,
    )


def _make_frame(width: int = 32, height: int = 24) -> FramePacket:
    depth = np.full((height, width), 1.0, dtype=np.float32)
    valid = np.ones((height, width), dtype=bool)

    return FramePacket(
        frame_id="frame-occ-01",
        timestamp_ns=1_000_000_000,
        rgb=np.zeros((height, width, 3), dtype=np.uint8),
        depth_m=depth,
        valid_depth_mask=valid,
        intrinsics=np.eye(3, dtype=np.float64),
        camera_to_shelf=np.eye(4, dtype=np.float64),
        source_type=SourceType.SYNTHETIC_RGBD,
    )


def test_occlusion_safety_clear_shelf() -> None:
    baseline = _make_baseline()
    frame = _make_frame()
    config = ShelfConfig(
        shelf_id="shelf-occ-01",
        roi_xyxy=(0, 0, 32, 24),
        bounds_min_m=(-0.5, -0.5, 0.4),
        bounds_max_m=(0.5, 0.5, 1.8),
        minimum_visible_fraction=0.70,
    )

    result = evaluate_occlusion_safety(frame, baseline, config)
    assert result.visible_shelf_fraction == pytest.approx(1.0)
    assert not result.is_occluded
    assert not result.person_present
    assert result.unoccluded_pixel_count == 32 * 24


def test_occlusion_safety_person_occlusion_suspends_confirmation() -> None:
    baseline = _make_baseline()
    frame = _make_frame()
    config = ShelfConfig(
        shelf_id="shelf-occ-01",
        roi_xyxy=(0, 0, 32, 24),
        bounds_min_m=(-0.5, -0.5, 0.4),
        bounds_max_m=(0.5, 0.5, 1.8),
        minimum_visible_fraction=0.70,
    )

    # Person occludes 12 rows out of 24 (50% of the shelf ROI)
    person_mask = np.zeros((24, 32), dtype=bool)
    person_mask[:12, :] = True

    result = evaluate_occlusion_safety(frame, baseline, config, person_occlusion_mask=person_mask)
    assert result.visible_shelf_fraction == pytest.approx(0.50)
    assert result.is_occluded  # 50% < 70% threshold
    assert result.person_present
    assert result.person_pixel_count == 12 * 32


def test_occlusion_safety_invalid_depth_triggers_occlusion() -> None:
    baseline = _make_baseline()
    frame = _make_frame()
    config = ShelfConfig(
        shelf_id="shelf-occ-01",
        roi_xyxy=(0, 0, 32, 24),
        bounds_min_m=(-0.5, -0.5, 0.4),
        bounds_max_m=(0.5, 0.5, 1.8),
        minimum_visible_fraction=0.70,
    )

    # Zero depth on 40% of the shelf
    frame.depth_m[:10, :] = 0.0
    frame.valid_depth_mask[:10, :] = False

    result = evaluate_occlusion_safety(frame, baseline, config)
    assert result.visible_shelf_fraction == pytest.approx(14.0 / 24.0)
    assert result.is_occluded
    assert not result.person_present

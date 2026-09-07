from __future__ import annotations

import numpy as np
import pytest

from kyra.contracts import BaselineArtifact, FramePacket, ShelfConfig, SourceType
from kyra.geometry.points import (
    project_camera_points_to_pixels,
    transform_points,
    unproject_depth_to_camera_points,
)
from kyra.geometry.registration import (
    estimate_rigid_transform,
    register_frame_to_baseline,
)


def _make_intrinsics(width: int = 64, height: int = 48) -> np.ndarray:
    return np.array(
        [
            [100.0, 0.0, width / 2.0],
            [0.0, 100.0, height / 2.0],
            [0.0, 0.0, 1.0],
        ],
        dtype=np.float64,
    )


def _make_shelf_config() -> ShelfConfig:
    return ShelfConfig(
        shelf_id="shelf-test-01",
        roi_xyxy=(8, 6, 56, 42),
        bounds_min_m=(-0.5, -0.5, 0.4),
        bounds_max_m=(0.5, 0.5, 1.8),
        registration_reject_m=0.02,
    )


def _make_baseline_and_frame(
    width: int = 64,
    height: int = 48,
    depth_val: float = 1.0,
) -> tuple[BaselineArtifact, FramePacket]:
    intrinsics = _make_intrinsics(width, height)
    cam_to_shelf = np.eye(4, dtype=np.float64)

    depth_m = np.full((height, width), depth_val, dtype=np.float32)
    valid_mask = np.ones((height, width), dtype=bool)

    # Fixed shelf structure on outer border of shelf ROI, center is portable
    fixed_mask = np.zeros((height, width), dtype=bool)
    fixed_mask[6:12, 8:56] = True
    fixed_mask[36:42, 8:56] = True
    fixed_mask[12:36, 8:16] = True
    fixed_mask[12:36, 48:56] = True

    occupancy = np.zeros((height, width, 1), dtype=np.uint8)
    occupancy[..., 0] = valid_mask.astype(np.uint8)

    baseline = BaselineArtifact(
        shelf_id="shelf-test-01",
        roi_xyxy=(8, 6, 56, 42),
        bounds_min_m=(-0.5, -0.5, 0.4),
        bounds_max_m=(0.5, 0.5, 1.8),
        baseline_depth_m=depth_m.copy(),
        valid_mask=valid_mask.copy(),
        fixed_geometry_mask=fixed_mask,
        portable_components=(),
        occupancy_grid=occupancy,
        noise_sigma_m=np.full((height, width), 0.002, dtype=np.float32),
        intrinsics=intrinsics,
        camera_to_shelf=cam_to_shelf,
        calibration_checksum="a" * 64,
    )

    frame = FramePacket(
        frame_id="frame-0001",
        timestamp_ns=1_000_000_000,
        rgb=np.zeros((height, width, 3), dtype=np.uint8),
        depth_m=depth_m.copy(),
        valid_depth_mask=valid_mask.copy(),
        intrinsics=intrinsics,
        camera_to_shelf=cam_to_shelf,
        source_type=SourceType.SYNTHETIC_RGBD,
    )

    return baseline, frame


def test_points_unproject_and_project_roundtrip() -> None:
    intrinsics = _make_intrinsics(64, 48)
    depth = np.full((48, 64), 1.25, dtype=np.float32)
    mask = np.zeros((48, 64), dtype=bool)
    mask[10:20, 15:25] = True

    points, rows, cols = unproject_depth_to_camera_points(depth, intrinsics, mask=mask)
    assert len(points) == 100
    assert np.allclose(points[:, 2], 1.25)

    u, v, z = project_camera_points_to_pixels(points, intrinsics)
    assert np.allclose(u, cols, atol=1e-5)
    assert np.allclose(v, rows, atol=1e-5)
    assert np.allclose(z, 1.25, atol=1e-5)


def test_transform_points_empty() -> None:
    empty = np.empty((0, 3), dtype=np.float64)
    result = transform_points(empty, np.eye(4, dtype=np.float64))
    assert result.shape == (0, 3)


def test_estimate_rigid_transform_identity() -> None:
    pts = np.array([[0.1, 0.2, 1.0], [0.3, 0.4, 1.0], [0.5, 0.6, 1.2]], dtype=np.float64)
    r_mat, t_vec, rot_deg, trans_m = estimate_rigid_transform(pts, pts)

    assert np.allclose(r_mat, np.eye(3), atol=1e-6)
    assert np.allclose(t_vec, np.zeros(3), atol=1e-6)
    assert rot_deg == pytest.approx(0.0, abs=1e-4)
    assert trans_m == pytest.approx((0.0, 0.0, 0.0), abs=1e-6)


def test_estimate_rigid_transform_translation_and_small_rotation() -> None:
    pts_src = np.array(
        [
            [-0.2, -0.2, 1.0],
            [0.2, -0.2, 1.0],
            [0.2, 0.2, 1.0],
            [-0.2, 0.2, 1.0],
            [0.0, 0.0, 1.1],
        ],
        dtype=np.float64,
    )
    # 0.5 degree rotation around Y axis
    angle = np.radians(0.5)
    r_true = np.array(
        [
            [np.cos(angle), 0, np.sin(angle)],
            [0, 1, 0],
            [-np.sin(angle), 0, np.cos(angle)],
        ],
        dtype=np.float64,
    )
    t_true = np.array([0.008, -0.005, 0.006], dtype=np.float64)
    pts_tgt = (pts_src @ r_true.T) + t_true

    r_est, t_est, rot_deg, trans_m = estimate_rigid_transform(pts_src, pts_tgt)
    assert rot_deg == pytest.approx(0.5, abs=1e-2)
    assert np.allclose(t_est, t_true, atol=1e-4)

    recovered = (pts_src @ r_est.T) + t_est
    assert np.allclose(recovered, pts_tgt, atol=1e-5)


def test_register_frame_to_baseline_zero_drift() -> None:
    baseline, frame = _make_baseline_and_frame()
    config = _make_shelf_config()

    result = register_frame_to_baseline(frame, baseline, config)
    assert not result.rejected
    assert result.rejection_reason is None
    assert result.residual_m == pytest.approx(0.0, abs=1e-6)
    assert result.rotation_deg == pytest.approx(0.0, abs=1e-4)
    assert result.translation_m == pytest.approx((0.0, 0.0, 0.0), abs=1e-6)
    assert result.corrected_depth_m is not None
    assert np.allclose(result.corrected_depth_m, frame.depth_m)


def test_register_frame_to_baseline_compensates_allowable_drift() -> None:
    baseline, frame = _make_baseline_and_frame(depth_val=1.0)
    config = _make_shelf_config()

    # Apply 10 mm depth shift to frame (within 15 mm envelope)
    frame.depth_m += 0.010
    result = register_frame_to_baseline(frame, baseline, config)

    assert not result.rejected
    assert result.rejection_reason is None
    assert result.residual_m < 0.005
    assert result.translation_m[2] == pytest.approx(-0.010, abs=1e-3)
    assert result.corrected_depth_m is not None
    # Corrected depth on fixed geometry should recover baseline depth (1.0m)
    fixed_mask = baseline.fixed_geometry_mask & (frame.valid_depth_mask)
    assert np.allclose(result.corrected_depth_m[fixed_mask], 1.0, atol=0.002)


def test_register_frame_to_baseline_rejects_drift_envelope_exceeded() -> None:
    baseline, frame = _make_baseline_and_frame(depth_val=1.0)
    config = _make_shelf_config()

    # Apply 25 mm translation (exceeds 15 mm envelope)
    frame.depth_m += 0.025
    result = register_frame_to_baseline(frame, baseline, config)

    assert result.rejected
    assert result.rejection_reason == "drift_envelope_exceeded"
    assert result.corrected_depth_m is None


def test_register_frame_to_baseline_rejects_excessive_residual() -> None:
    baseline, frame = _make_baseline_and_frame(depth_val=1.0)
    config = _make_shelf_config()

    # Apply strong non-rigid distortion with high residual > 20 mm
    h, w = frame.depth_m.shape
    y_coords, x_coords = np.indices((h, w))
    distortion = 0.035 * np.sign(np.sin(x_coords / 2.0))
    frame.depth_m += distortion.astype(np.float32)

    result = register_frame_to_baseline(
        frame,
        baseline,
        config,
        max_envelope_translation_m=0.10,
        max_envelope_rotation_deg=45.0,
    )
    assert result.rejected
    assert result.rejection_reason == "registration_residual_exceeded"
    assert result.residual_m > config.registration_reject_m
    assert result.corrected_depth_m is None


def test_register_frame_to_baseline_rejects_insufficient_points() -> None:
    baseline, frame = _make_baseline_and_frame()
    config = _make_shelf_config()

    # Zero out fixed geometry mask so fewer than min_fixed_points are available
    baseline.fixed_geometry_mask[:] = False
    result = register_frame_to_baseline(frame, baseline, config)

    assert result.rejected
    assert result.rejection_reason == "insufficient_fixed_geometry_points"
    assert result.fixed_point_count == 0
    assert result.corrected_depth_m is None

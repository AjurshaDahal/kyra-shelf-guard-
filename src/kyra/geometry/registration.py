"""Shelf-only registration and camera drift check for Person 2."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from kyra.contracts import BaselineArtifact, FramePacket, ShelfConfig
from kyra.geometry.points import unproject_depth_to_camera_points

# Default drift envelope per assignment specification
MAX_ENVELOPE_TRANSLATION_M = 0.015  # 15 mm
MAX_ENVELOPE_ROTATION_DEG = 1.0    # 1.0 degree


@dataclass(slots=True, frozen=True)
class RegistrationResult:
    """Result of registering an observation frame against baseline fixed geometry."""

    rejected: bool
    residual_m: float
    transform_camera_to_corrected: np.ndarray
    translation_m: tuple[float, float, float]
    rotation_deg: float
    fixed_point_count: int
    rejection_reason: str | None = None
    corrected_depth_m: np.ndarray | None = None


def estimate_rigid_transform(
    source_points: np.ndarray,
    target_points: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, float, tuple[float, float, float]]:
    """Estimate optimal 3D rigid transform [R | t] aligning source to target using SVD (Kabsch).

    Returns:
        R: 3x3 rotation matrix.
        t: 3-element translation vector.
        rotation_deg: Rotation angle in degrees.
        translation_m: Translation vector as (tx, ty, tz) tuple.
    """
    if len(source_points) < 3 or len(target_points) < 3:
        return np.eye(3, dtype=np.float64), np.zeros(3, dtype=np.float64), 0.0, (0.0, 0.0, 0.0)

    centroid_src = np.mean(source_points, axis=0)
    centroid_tgt = np.mean(target_points, axis=0)

    src_centered = source_points - centroid_src
    tgt_centered = target_points - centroid_tgt

    h_matrix = src_centered.T @ tgt_centered
    u, _, vt = np.linalg.svd(h_matrix)

    r_matrix = vt.T @ u.T
    # Handle reflection
    if np.linalg.det(r_matrix) < 0:
        vt[-1, :] *= -1
        r_matrix = vt.T @ u.T

    t_vec = centroid_tgt - r_matrix @ centroid_src

    # Calculate rotation angle in degrees
    trace_val = float(np.trace(r_matrix))
    cos_angle = np.clip((trace_val - 1.0) / 2.0, -1.0, 1.0)
    rotation_deg = float(np.degrees(np.arccos(cos_angle)))
    translation_m = (float(t_vec[0]), float(t_vec[1]), float(t_vec[2]))

    return r_matrix, t_vec, rotation_deg, translation_m


def register_frame_to_baseline(
    current_frame: FramePacket,
    baseline: BaselineArtifact,
    shelf_config: ShelfConfig,
    *,
    max_envelope_translation_m: float = MAX_ENVELOPE_TRANSLATION_M,
    max_envelope_rotation_deg: float = MAX_ENVELOPE_ROTATION_DEG,
    min_fixed_points: int = 16,
) -> RegistrationResult:
    """Register current frame against fixed baseline geometry and detect camera drift.

    Args:
        current_frame: Incoming observation frame.
        baseline: Opening shelf baseline artifact.
        shelf_config: Shelf configuration including ROI and registration thresholds.
        max_envelope_translation_m: Maximum correctable translation drift (default 15 mm).
        max_envelope_rotation_deg: Maximum correctable rotation drift (default 1.0 degree).
        min_fixed_points: Minimum number of valid fixed pixels required.

    Returns:
        RegistrationResult indicating whether the frame is accepted or rejected,
        the registration residual in metres, and optional corrected depth.
    """
    x1, y1, x2, y2 = shelf_config.roi_xyxy
    h, w = baseline.baseline_depth_m.shape

    roi_mask = np.zeros((h, w), dtype=bool)
    roi_mask[max(0, y1) : min(h, y2), max(0, x1) : min(w, x2)] = True

    # Fixed shelf pixels that are valid in both baseline and current frame
    fixed_eval_mask = (
        roi_mask
        & baseline.fixed_geometry_mask
        & baseline.valid_mask
        & current_frame.valid_depth_mask
    )

    fixed_count = int(np.count_nonzero(fixed_eval_mask))
    if fixed_count < min_fixed_points:
        return RegistrationResult(
            rejected=True,
            residual_m=float("inf"),
            transform_camera_to_corrected=np.eye(4, dtype=np.float64),
            translation_m=(0.0, 0.0, 0.0),
            rotation_deg=0.0,
            fixed_point_count=fixed_count,
            rejection_reason="insufficient_fixed_geometry_points",
            corrected_depth_m=None,
        )

    # Unproject fixed points from baseline and current frame
    curr_pts, _, _ = unproject_depth_to_camera_points(
        current_frame.depth_m,
        current_frame.intrinsics,
        mask=fixed_eval_mask,
    )
    base_pts, _, _ = unproject_depth_to_camera_points(
        baseline.baseline_depth_m,
        baseline.intrinsics,
        mask=fixed_eval_mask,
    )

    if len(curr_pts) != len(base_pts) or len(curr_pts) < min_fixed_points:
        return RegistrationResult(
            rejected=True,
            residual_m=float("inf"),
            transform_camera_to_corrected=np.eye(4, dtype=np.float64),
            translation_m=(0.0, 0.0, 0.0),
            rotation_deg=0.0,
            fixed_point_count=len(curr_pts),
            rejection_reason="insufficient_fixed_geometry_points",
            corrected_depth_m=None,
        )

    # Estimate 3D rigid transform from current to baseline
    r_mat, t_vec, rot_deg, trans_m = estimate_rigid_transform(curr_pts, base_pts)

    transform_4x4 = np.eye(4, dtype=np.float64)
    transform_4x4[:3, :3] = r_mat
    transform_4x4[:3, 3] = t_vec

    # Align current fixed points to baseline
    aligned_pts = (curr_pts @ r_mat.T) + t_vec
    residuals = np.linalg.norm(aligned_pts - base_pts, axis=1)
    residual_m = float(np.mean(residuals))

    # Reject if drift exceeds allowable test envelope (> 15 mm or > 1 degree)
    trans_norm = float(np.linalg.norm(t_vec))
    if trans_norm > max_envelope_translation_m or rot_deg > max_envelope_rotation_deg:
        return RegistrationResult(
            rejected=True,
            residual_m=residual_m,
            transform_camera_to_corrected=transform_4x4,
            translation_m=trans_m,
            rotation_deg=rot_deg,
            fixed_point_count=fixed_count,
            rejection_reason="drift_envelope_exceeded",
            corrected_depth_m=None,
        )

    # Reject if post-alignment residual exceeds registration threshold (default 2 cm)
    reject_threshold = shelf_config.registration_reject_m
    if residual_m > reject_threshold:
        return RegistrationResult(
            rejected=True,
            residual_m=residual_m,
            transform_camera_to_corrected=transform_4x4,
            translation_m=trans_m,
            rotation_deg=rot_deg,
            fixed_point_count=fixed_count,
            rejection_reason="registration_residual_exceeded",
            corrected_depth_m=None,
        )

    # Within envelope and threshold: compute corrected depth map for valid pixels
    corrected_depth = current_frame.depth_m.copy()
    all_pts, all_rows, all_cols = unproject_depth_to_camera_points(
        current_frame.depth_m,
        current_frame.intrinsics,
        mask=current_frame.valid_depth_mask,
    )
    if len(all_pts) > 0:
        aligned_all = (all_pts @ r_mat.T) + t_vec
        corrected_depth[all_rows, all_cols] = np.maximum(0.0, aligned_all[:, 2]).astype(np.float32)

    return RegistrationResult(
        rejected=False,
        residual_m=residual_m,
        transform_camera_to_corrected=transform_4x4,
        translation_m=trans_m,
        rotation_deg=rot_deg,
        fixed_point_count=fixed_count,
        rejection_reason=None,
        corrected_depth_m=corrected_depth,
    )

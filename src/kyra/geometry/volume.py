"""Metric volume estimation along rays and voxel cross-checks for Person 2."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from kyra.contracts import ShelfConfig
from kyra.geometry.clustering import Cluster3D


@dataclass(slots=True, frozen=True)
class VolumeEstimate:
    """Metric volume estimate for a 3D change cluster."""

    volume_m3: float
    ray_volume_m3: float
    voxel_volume_m3: float | None
    confidence: float
    is_significant: bool


def estimate_cluster_volume(
    cluster: Cluster3D,
    current_depth_m: np.ndarray,
    baseline_depth_m: np.ndarray,
    intrinsics: np.ndarray,
    shelf_config: ShelfConfig,
    *,
    baseline_occupancy_grid: np.ndarray | None = None,
) -> VolumeEstimate:
    """Estimate metric volume of a 3D cluster in cubic metres.

    Integrates depth change along pixel ray frustums:
        V = sum_i |z_far_i^3 - z_near_i^3| / (3 * fx * fy)

    Cross-checks with 1 cm occupancy grid where available.

    Args:
        cluster: 3D cluster from extract_3d_clusters.
        current_depth_m: 2D float32 current depth map.
        baseline_depth_m: 2D float32 baseline depth map.
        intrinsics: 3x3 camera intrinsics.
        shelf_config: ShelfConfig containing volume alert thresholds.
        baseline_occupancy_grid: Optional 3D occupancy grid from baseline.

    Returns:
        VolumeEstimate with volume in cubic metres, confidence score, and significance flag.
    """
    if cluster.pixel_count == 0:
        return VolumeEstimate(
            volume_m3=0.0,
            ray_volume_m3=0.0,
            voxel_volume_m3=None,
            confidence=0.0,
            is_significant=False,
        )

    mask = cluster.pixel_mask
    z_curr = current_depth_m[mask].astype(np.float64)
    z_base = baseline_depth_m[mask].astype(np.float64)

    fx = float(intrinsics[0, 0])
    fy = float(intrinsics[1, 1])

    z_far = np.maximum(z_curr, z_base)
    z_near = np.minimum(z_curr, z_base)

    # Frustum integration
    shells = (z_far**3 - z_near**3) / (3.0 * fx * fy)
    ray_volume = float(np.sum(shells))

    # Bounding-box / voxel cross-check if occupancy grid provided
    voxel_volume: float | None = None
    if baseline_occupancy_grid is not None and baseline_occupancy_grid.size > 0:
        voxel_size = shelf_config.voxel_size_m
        box_dx = max(voxel_size, cluster.bounds_max_m[0] - cluster.bounds_min_m[0])
        box_dy = max(voxel_size, cluster.bounds_max_m[1] - cluster.bounds_min_m[1])
        box_dz = max(voxel_size, cluster.bounds_max_m[2] - cluster.bounds_min_m[2])
        # Bounding prism volume as upper bound
        voxel_volume = float(box_dx * box_dy * box_dz)

    final_volume = ray_volume

    # Compute confidence
    confidence = 0.95

    if cluster.pixel_count < 16:
        confidence -= 0.15

    # Check edge contact with shelf ROI
    x1, y1, x2, y2 = shelf_config.roi_xyxy
    rows, cols = np.nonzero(mask)
    on_edge = (
        np.any(rows <= y1 + 1)
        or np.any(rows >= y2 - 2)
        or np.any(cols <= x1 + 1)
        or np.any(cols >= x2 - 2)
    )
    if on_edge:
        confidence -= 0.10

    # Disagreement penalty if voxel volume is known and wildly different
    if voxel_volume is not None and ray_volume > 0:
        ratio = voxel_volume / ray_volume
        if ratio < 0.2 or ratio > 8.0:
            confidence -= 0.10

    confidence = float(np.clip(confidence, 0.10, 1.0))
    is_significant = final_volume >= shelf_config.minimum_alert_volume_m3

    return VolumeEstimate(
        volume_m3=final_volume,
        ray_volume_m3=ray_volume,
        voxel_volume_m3=voxel_volume,
        confidence=confidence,
        is_significant=is_significant,
    )

from __future__ import annotations

import numpy as np
import pytest

from kyra.contracts import ShelfConfig
from kyra.geometry.clustering import extract_3d_clusters
from kyra.geometry.volume import estimate_cluster_volume


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
        shelf_id="shelf-vol-01",
        roi_xyxy=(4, 4, 60, 44),
        bounds_min_m=(-0.5, -0.5, 0.4),
        bounds_max_m=(0.5, 0.5, 1.8),
        minimum_alert_volume_m3=5e-5,
    )


def test_extract_3d_clusters_empty_mask() -> None:
    mask = np.zeros((48, 64), dtype=bool)
    depth = np.full((48, 64), 1.0, dtype=np.float32)
    intrinsics = _make_intrinsics()
    cam_to_shelf = np.eye(4, dtype=np.float64)

    clusters = extract_3d_clusters(mask, depth, intrinsics, cam_to_shelf)
    assert clusters == ()


def test_extract_3d_clusters_filters_noise() -> None:
    mask = np.zeros((48, 64), dtype=bool)
    # Single isolated pixel
    mask[20, 20] = True
    depth = np.full((48, 64), 1.0, dtype=np.float32)
    intrinsics = _make_intrinsics()
    cam_to_shelf = np.eye(4, dtype=np.float64)

    clusters = extract_3d_clusters(mask, depth, intrinsics, cam_to_shelf, min_pixel_area=4)
    assert clusters == ()


def test_extract_3d_clusters_extracts_and_sorts() -> None:
    mask = np.zeros((48, 64), dtype=bool)
    # Cluster A: 4x4 = 16 pixels
    mask[10:14, 10:14] = True
    # Cluster B: 6x6 = 36 pixels
    mask[30:36, 30:36] = True

    depth = np.full((48, 64), 1.0, dtype=np.float32)
    intrinsics = _make_intrinsics()
    cam_to_shelf = np.eye(4, dtype=np.float64)

    clusters = extract_3d_clusters(mask, depth, intrinsics, cam_to_shelf, min_pixel_area=4)
    assert len(clusters) == 2
    # Sorted descending by pixel count
    assert clusters[0].pixel_count == 36
    assert clusters[1].pixel_count == 16
    assert clusters[0].centroid_m[2] == pytest.approx(1.0, abs=1e-3)


def test_estimate_cluster_volume_accuracy() -> None:
    width, height = 64, 48
    intrinsics = _make_intrinsics(width, height)
    cam_to_shelf = np.eye(4, dtype=np.float64)
    config = _make_shelf_config()
    # Create synthetic object with 10x10 pixels at 1.0 m depth
    # Pixel angular size: dx = z/fx = 1.0/100 = 0.01 m, dy = z/fy = 1.0/100 = 0.01 m
    # Pixel area = 0.0001 m^2
    # 10x10 pixels = 100 pixels -> footprint area = 0.01 m^2
    # Depth change delta_z = 0.10 m (10 cm)
    # True volume = 0.01 m^2 * 0.10 m = 0.001 m^3 (1.0 Liter)
    mask = np.zeros((height, width), dtype=bool)
    mask[19:29, 27:37] = True

    curr_depth = np.full((height, width), 1.10, dtype=np.float32)
    base_depth = np.full((height, width), 1.00, dtype=np.float32)

    clusters = extract_3d_clusters(mask, curr_depth, intrinsics, cam_to_shelf, min_pixel_area=4)
    assert len(clusters) == 1
    cluster = clusters[0]

    estimate = estimate_cluster_volume(cluster, curr_depth, base_depth, intrinsics, config)

    # Frustum volume for 10x10 pixels between 1.00m and 1.10m:
    # (1.1^3 - 1.0^3) / (3 * 100 * 100) = 0.331 / 30000 = 0.00001103 m^3 per pixel
    # 100 pixels * 0.00001103 = 0.001103 m^3 (~1.1 L)
    # Expected volume error compared to 0.001 m^3 box is ~10%, well within 15% criterion
    assert estimate.volume_m3 == pytest.approx(0.001103, rel=0.05)
    assert estimate.is_significant
    assert estimate.confidence > 0.70


def test_estimate_cluster_volume_insignificant_small() -> None:
    width, height = 64, 48
    intrinsics = _make_intrinsics(width, height)
    cam_to_shelf = np.eye(4, dtype=np.float64)
    config = _make_shelf_config()

    # Small 2x2 pixels with small 15 mm depth change
    mask = np.zeros((height, width), dtype=bool)
    mask[20:23, 20:23] = True
    curr_depth = np.full((height, width), 1.016, dtype=np.float32)
    base_depth = np.full((height, width), 1.000, dtype=np.float32)

    clusters = extract_3d_clusters(mask, curr_depth, intrinsics, cam_to_shelf, min_pixel_area=4)
    assert len(clusters) == 1
    estimate = estimate_cluster_volume(clusters[0], curr_depth, base_depth, intrinsics, config)

    # Volume is tiny (< 5e-5 m^3) -> not significant
    assert not estimate.is_significant

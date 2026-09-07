"""3D connected-component clustering for Person 2 geometry."""

from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np

from kyra.geometry.points import transform_points, unproject_depth_to_camera_points


@dataclass(slots=True, frozen=True)
class Cluster3D:
    """A 3D spatial cluster of depth change pixels."""

    cluster_id: int
    pixel_count: int
    pixel_mask: np.ndarray
    camera_points: np.ndarray
    shelf_points: np.ndarray
    centroid_m: tuple[float, float, float]
    bounds_min_m: tuple[float, float, float]
    bounds_max_m: tuple[float, float, float]


def extract_3d_clusters(
    candidate_mask: np.ndarray,
    depth_m: np.ndarray,
    intrinsics: np.ndarray,
    camera_to_shelf: np.ndarray,
    *,
    min_pixel_area: int = 4,
) -> tuple[Cluster3D, ...]:
    """Extract, filter, and unproject 3D clusters from a 2D candidate mask.

    Applies morphological filtering to eliminate single-pixel noise and bridge
    narrow gaps, labels 2D connected components, and projects each valid cluster
    into 3D camera and shelf coordinates.

    Args:
        candidate_mask: 2D boolean candidate mask (e.g. from signed diff).
        depth_m: 2D float32 depth in metres.
        intrinsics: 3x3 camera intrinsics matrix.
        camera_to_shelf: 4x4 transform from camera to shelf coordinates.
        min_pixel_area: Minimum connected-component pixel count.

    Returns:
        Tuple of Cluster3D objects sorted by descending pixel count.
    """
    if not np.any(candidate_mask):
        return ()

    mask_uint8 = candidate_mask.astype(np.uint8) * 255
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))

    # Morphological opening (noise removal) then closing (small gap filling)
    cleaned = cv2.morphologyEx(mask_uint8, cv2.MORPH_OPEN, kernel)
    cleaned = cv2.morphologyEx(cleaned, cv2.MORPH_CLOSE, kernel)

    num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(cleaned, connectivity=8)

    clusters: list[Cluster3D] = []

    for label_idx in range(1, num_labels):  # Skip background (0)
        area = int(stats[label_idx, cv2.CC_STAT_AREA])
        if area < min_pixel_area:
            continue

        comp_mask = labels == label_idx
        cam_pts, _, _ = unproject_depth_to_camera_points(depth_m, intrinsics, mask=comp_mask)

        if len(cam_pts) == 0:
            continue

        shelf_pts = transform_points(cam_pts, camera_to_shelf)

        centroid = np.mean(shelf_pts, axis=0)
        bounds_min = np.min(shelf_pts, axis=0)
        bounds_max = np.max(shelf_pts, axis=0)

        clusters.append(
            Cluster3D(
                cluster_id=label_idx,
                pixel_count=len(cam_pts),
                pixel_mask=comp_mask,
                camera_points=cam_pts,
                shelf_points=shelf_pts,
                centroid_m=(float(centroid[0]), float(centroid[1]), float(centroid[2])),
                bounds_min_m=(float(bounds_min[0]), float(bounds_min[1]), float(bounds_min[2])),
                bounds_max_m=(float(bounds_max[0]), float(bounds_max[1]), float(bounds_max[2])),
            )
        )

    # Sort descending by pixel count
    clusters.sort(key=lambda c: c.pixel_count, reverse=True)
    return tuple(clusters)

"""3D point and projection utilities for Person 2 geometry."""

from __future__ import annotations

import numpy as np


def unproject_depth_to_camera_points(
    depth_m: np.ndarray,
    intrinsics: np.ndarray,
    mask: np.ndarray | None = None,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Unproject depth map to 3D points in camera coordinates.

    Returns:
        points: (N, 3) float64 array of [X, Y, Z] in camera frame.
        rows: (N,) int array of y-coordinates in image frame.
        cols: (N,) int array of x-coordinates in image frame.
    """
    if mask is None:
        valid = np.isfinite(depth_m) & (depth_m > 0)
    else:
        valid = mask & np.isfinite(depth_m) & (depth_m > 0)

    rows, cols = np.nonzero(valid)
    if len(rows) == 0:
        return (
            np.empty((0, 3), dtype=np.float64),
            np.empty((0,), dtype=np.int64),
            np.empty((0,), dtype=np.int64),
        )

    z = depth_m[rows, cols].astype(np.float64)
    fx = float(intrinsics[0, 0])
    fy = float(intrinsics[1, 1])
    cx = float(intrinsics[0, 2])
    cy = float(intrinsics[1, 2])

    x = (cols.astype(np.float64) - cx) * z / fx
    y = (rows.astype(np.float64) - cy) * z / fy

    points = np.column_stack((x, y, z))
    return points, rows, cols


def transform_points(points: np.ndarray, transform_4x4: np.ndarray) -> np.ndarray:
    """Transform 3D points using a 4x4 homogeneous matrix."""
    if len(points) == 0:
        return np.empty((0, 3), dtype=np.float64)

    homogeneous = np.column_stack((points, np.ones(len(points), dtype=np.float64)))
    transformed = (homogeneous @ transform_4x4.T)[:, :3]
    return np.ascontiguousarray(transformed, dtype=np.float64)


def project_camera_points_to_pixels(
    points: np.ndarray,
    intrinsics: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Project 3D camera points to 2D image coordinates (u, v) and depth z."""
    if len(points) == 0:
        return (
            np.empty((0,), dtype=np.float64),
            np.empty((0,), dtype=np.float64),
            np.empty((0,), dtype=np.float64),
        )

    fx = float(intrinsics[0, 0])
    fy = float(intrinsics[1, 1])
    cx = float(intrinsics[0, 2])
    cy = float(intrinsics[1, 2])

    z = points[:, 2]
    valid_z = z > 1e-6
    u = np.zeros(len(points), dtype=np.float64)
    v = np.zeros(len(points), dtype=np.float64)

    u[valid_z] = (points[valid_z, 0] * fx / z[valid_z]) + cx
    v[valid_z] = (points[valid_z, 1] * fy / z[valid_z]) + cy

    return u, v, z

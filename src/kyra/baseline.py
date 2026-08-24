"""Opening-time shelf calibration and baseline artifact persistence."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np

from kyra.contracts import (
    SCHEMA_VERSION,
    BaselineArtifact,
    FramePacket,
    PortableComponent,
    ShelfConfig,
    SourceType,
)


def _roi_mask(shape: tuple[int, int], roi: tuple[int, int, int, int]) -> np.ndarray:
    height, width = shape
    x1, y1, x2, y2 = roi
    if x1 < 0 or y1 < 0 or x2 > width or y2 > height:
        raise ValueError(f"shelf ROI {roi} is outside frame shape {shape}")
    result = np.zeros(shape, dtype=bool)
    result[y1:y2, x1:x2] = True
    return result


def _camera_points(
    depth_m: np.ndarray, intrinsics: np.ndarray, mask: np.ndarray
) -> np.ndarray:
    rows, cols = np.nonzero(mask)
    if len(rows) == 0:
        return np.empty((0, 3), dtype=np.float64)
    z = depth_m[rows, cols].astype(np.float64)
    fx, fy = intrinsics[0, 0], intrinsics[1, 1]
    cx, cy = intrinsics[0, 2], intrinsics[1, 2]
    x = (cols.astype(np.float64) - cx) * z / fx
    y = (rows.astype(np.float64) - cy) * z / fy
    return np.column_stack((x, y, z))


def _transform_points(points: np.ndarray, transform: np.ndarray) -> np.ndarray:
    if not len(points):
        return points
    homogeneous = np.column_stack((points, np.ones(len(points), dtype=np.float64)))
    return (homogeneous @ transform.T)[:, :3]


def _frustum_volume(
    near_depth_m: np.ndarray,
    far_depth_m: float | np.ndarray,
    mask: np.ndarray,
    intrinsics: np.ndarray,
) -> float:
    """Integrate a pixel ray frustum using its small-angle solid angle."""
    near = near_depth_m[mask].astype(np.float64)
    if np.isscalar(far_depth_m):
        far = np.full_like(near, float(far_depth_m))
    else:
        far = np.asarray(far_depth_m)[mask].astype(np.float64)
    positive = far > near
    if not np.any(positive):
        return 0.0
    fx, fy = float(intrinsics[0, 0]), float(intrinsics[1, 1])
    shells = (far[positive] ** 3 - near[positive] ** 3) / (3.0 * fx * fy)
    return float(np.sum(shells))


def _dominant_depth(depth: np.ndarray, mask: np.ndarray) -> float:
    samples = depth[mask]
    if len(samples) < 16:
        raise ValueError("not enough valid shelf pixels to estimate the shelf plane")
    # Five-millimetre bins make this stable under sensor quantisation/noise while
    # still separating an item from its back plane by the 15 mm decision floor.
    bins = np.round(samples.astype(np.float64) / 0.005).astype(np.int32)
    values, counts = np.unique(bins, return_counts=True)
    return float(values[np.argmax(counts)] * 0.005)


def _checksum(
    baseline_depth_m: np.ndarray,
    valid_mask: np.ndarray,
    intrinsics: np.ndarray,
    camera_to_shelf: np.ndarray,
    shelf_config: ShelfConfig,
) -> str:
    digest = hashlib.sha256()
    for array in (baseline_depth_m, valid_mask, intrinsics, camera_to_shelf):
        contiguous = np.ascontiguousarray(array)
        digest.update(str(contiguous.dtype).encode("ascii"))
        digest.update(str(contiguous.shape).encode("ascii"))
        digest.update(contiguous.tobytes())
    digest.update(
        json.dumps(
            {
                "shelf_id": shelf_config.shelf_id,
                "roi_xyxy": shelf_config.roi_xyxy,
                "bounds_min_m": shelf_config.bounds_min_m,
                "bounds_max_m": shelf_config.bounds_max_m,
                "voxel_size_m": shelf_config.voxel_size_m,
            },
            sort_keys=True,
        ).encode("utf-8")
    )
    return digest.hexdigest()


class BaselineBuilder:
    """Fuse unobstructed RGB-D frames into a calibrated shelf artifact."""

    def __init__(self, *, minimum_frames: int = 30) -> None:
        if minimum_frames < 1:
            raise ValueError("minimum_frames must be positive")
        self.minimum_frames = minimum_frames

    def fit(
        self, frames: Iterable[FramePacket], shelf_config: ShelfConfig
    ) -> BaselineArtifact:
        packets = list(frames)
        if len(packets) < self.minimum_frames:
            raise ValueError(
                f"baseline requires at least {self.minimum_frames} frames; got {len(packets)}"
            )
        shape = packets[0].depth_m.shape
        if any(packet.depth_m.shape != shape for packet in packets):
            raise ValueError("all calibration frames must have the same resolution")
        if any(not np.allclose(packet.intrinsics, packets[0].intrinsics) for packet in packets):
            raise ValueError("camera intrinsics changed during baseline calibration")

        samples = np.stack(
            [
                np.where(packet.valid_depth_mask, packet.depth_m, np.nan)
                for packet in packets
            ],
            axis=0,
        ).astype(np.float32)
        with np.errstate(invalid="ignore"):
            baseline_depth = np.nanmedian(samples, axis=0).astype(np.float32)
            absolute_deviation = np.abs(samples - baseline_depth[None, :, :])
            noise_sigma = (1.4826 * np.nanmedian(absolute_deviation, axis=0)).astype(
                np.float32
            )

        valid_count = np.sum(np.isfinite(samples), axis=0)
        required_count = max(1, int(np.ceil(0.8 * len(packets))))
        valid_mask = (valid_count >= required_count) & np.isfinite(baseline_depth)
        baseline_depth[~valid_mask] = 0.0
        noise_sigma[~np.isfinite(noise_sigma)] = 0.0
        # A one-millimetre floor reflects depth quantisation and prevents zero-noise
        # synthetic pixels from becoming unrealistically sensitive.
        noise_sigma[valid_mask] = np.maximum(noise_sigma[valid_mask], 0.001)

        roi = _roi_mask(shape, shelf_config.roi_xyxy)
        shelf_valid = valid_mask & roi
        plane_depth = _dominant_depth(baseline_depth, shelf_valid)
        fixed_tolerance = np.maximum(
            shelf_config.removal_floor_m, 3.0 * noise_sigma
        )
        fixed_mask = shelf_valid & (
            np.abs(baseline_depth - plane_depth) <= fixed_tolerance
        )
        portable_candidate = (
            shelf_valid
            & ~fixed_mask
            & (baseline_depth < plane_depth - fixed_tolerance)
        )
        portable_candidate = cv2.morphologyEx(
            portable_candidate.astype(np.uint8),
            cv2.MORPH_OPEN,
            np.ones((3, 3), dtype=np.uint8),
        ).astype(bool)

        components: list[PortableComponent] = []
        count, labels, stats, _ = cv2.connectedComponentsWithStats(
            portable_candidate.astype(np.uint8), connectivity=8
        )
        for label in range(1, count):
            if stats[label, cv2.CC_STAT_AREA] < 4:
                continue
            component_mask = labels == label
            volume = _frustum_volume(
                baseline_depth, plane_depth, component_mask, packets[0].intrinsics
            )
            if volume <= 0 or volume >= shelf_config.portable_max_volume_m3:
                continue
            near_points = _camera_points(
                baseline_depth, packets[0].intrinsics, component_mask
            )
            far_depth = np.where(component_mask, plane_depth, 0).astype(np.float32)
            far_points = _camera_points(far_depth, packets[0].intrinsics, component_mask)
            points = _transform_points(
                np.vstack((near_points, far_points)), packets[0].camera_to_shelf
            )
            bounds_min = tuple(float(value) for value in np.min(points, axis=0))
            bounds_max = tuple(float(value) for value in np.max(points, axis=0))
            components.append(
                PortableComponent(
                    component_id=f"portable-{len(components) + 1:03d}",
                    volume_m3=volume,
                    bounds_min_m=bounds_min,
                    bounds_max_m=bounds_max,
                    pixel_count=int(np.count_nonzero(component_mask)),
                )
            )

        occupancy = self._occupancy_grid(
            baseline_depth,
            shelf_valid,
            packets[0].intrinsics,
            packets[0].camera_to_shelf,
            shelf_config,
        )
        checksum = _checksum(
            baseline_depth,
            valid_mask,
            packets[0].intrinsics,
            packets[0].camera_to_shelf,
            shelf_config,
        )
        approximate_metric = any(
            packet.source_type is SourceType.MIDAS_ALIGNED for packet in packets
        )
        return BaselineArtifact(
            shelf_id=shelf_config.shelf_id,
            roi_xyxy=shelf_config.roi_xyxy,
            bounds_min_m=shelf_config.bounds_min_m,
            bounds_max_m=shelf_config.bounds_max_m,
            baseline_depth_m=baseline_depth,
            valid_mask=valid_mask,
            fixed_geometry_mask=fixed_mask,
            portable_components=tuple(components),
            occupancy_grid=occupancy,
            noise_sigma_m=noise_sigma,
            intrinsics=packets[0].intrinsics,
            camera_to_shelf=packets[0].camera_to_shelf,
            calibration_checksum=checksum,
            approximate_metric=approximate_metric,
            metadata={
                "calibration_frame_count": len(packets),
                "plane_depth_m": plane_depth,
                "valid_pixel_fraction": float(np.mean(shelf_valid[roi])),
                "noise_model": "temporal_median_and_scaled_MAD",
            },
        )

    @staticmethod
    def _occupancy_grid(
        depth_m: np.ndarray,
        valid_mask: np.ndarray,
        intrinsics: np.ndarray,
        camera_to_shelf: np.ndarray,
        shelf_config: ShelfConfig,
    ) -> np.ndarray:
        minimum = np.asarray(shelf_config.bounds_min_m, dtype=np.float64)
        maximum = np.asarray(shelf_config.bounds_max_m, dtype=np.float64)
        shape = np.ceil((maximum - minimum) / shelf_config.voxel_size_m).astype(int)
        if np.any(shape <= 0) or np.prod(shape, dtype=np.int64) > 100_000_000:
            raise ValueError(f"unsafe occupancy-grid dimensions: {tuple(shape)}")
        grid = np.zeros(tuple(int(value) for value in shape), dtype=np.uint8)
        points = _transform_points(
            _camera_points(depth_m, intrinsics, valid_mask), camera_to_shelf
        )
        indices = np.floor((points - minimum) / shelf_config.voxel_size_m).astype(int)
        inside = np.all((indices >= 0) & (indices < shape), axis=1)
        indices = indices[inside]
        if len(indices):
            grid[indices[:, 0], indices[:, 1], indices[:, 2]] = 1
        return grid


def _metadata_path(npz_path: Path) -> Path:
    return npz_path.with_suffix(".json")


def save_baseline(artifact: BaselineArtifact, path: str | Path) -> tuple[Path, Path]:
    """Store an artifact as compressed arrays plus human-readable metadata."""
    npz_path = Path(path)
    if npz_path.suffix.lower() != ".npz":
        npz_path = npz_path.with_suffix(".npz")
    npz_path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        npz_path,
        baseline_depth_m=artifact.baseline_depth_m,
        valid_mask=artifact.valid_mask.astype(np.uint8),
        fixed_geometry_mask=artifact.fixed_geometry_mask.astype(np.uint8),
        occupancy_grid=artifact.occupancy_grid,
        noise_sigma_m=artifact.noise_sigma_m,
        intrinsics=artifact.intrinsics,
        camera_to_shelf=artifact.camera_to_shelf,
    )
    metadata = {
        "schema_version": artifact.schema_version,
        "shelf_id": artifact.shelf_id,
        "roi_xyxy": artifact.roi_xyxy,
        "bounds_min_m": artifact.bounds_min_m,
        "bounds_max_m": artifact.bounds_max_m,
        "calibration_checksum": artifact.calibration_checksum,
        "approximate_metric": artifact.approximate_metric,
        "portable_components": [
            {
                "component_id": component.component_id,
                "volume_m3": component.volume_m3,
                "bounds_min_m": component.bounds_min_m,
                "bounds_max_m": component.bounds_max_m,
                "pixel_count": component.pixel_count,
            }
            for component in artifact.portable_components
        ],
        "metadata": artifact.metadata,
    }
    json_path = _metadata_path(npz_path)
    json_path.write_text(
        json.dumps(metadata, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return npz_path, json_path


def load_baseline(path: str | Path) -> BaselineArtifact:
    npz_path = Path(path)
    if npz_path.suffix.lower() != ".npz":
        npz_path = npz_path.with_suffix(".npz")
    metadata = json.loads(_metadata_path(npz_path).read_text(encoding="utf-8"))
    if metadata["schema_version"] != SCHEMA_VERSION:
        raise ValueError(
            f"unsupported baseline schema {metadata['schema_version']!r}; "
            f"expected {SCHEMA_VERSION!r}"
        )
    with np.load(npz_path, allow_pickle=False) as arrays:
        return BaselineArtifact(
            shelf_id=metadata["shelf_id"],
            roi_xyxy=tuple(metadata["roi_xyxy"]),
            bounds_min_m=tuple(metadata["bounds_min_m"]),
            bounds_max_m=tuple(metadata["bounds_max_m"]),
            baseline_depth_m=arrays["baseline_depth_m"],
            valid_mask=arrays["valid_mask"].astype(bool),
            fixed_geometry_mask=arrays["fixed_geometry_mask"].astype(bool),
            portable_components=tuple(
                PortableComponent(
                    component_id=record["component_id"],
                    volume_m3=float(record["volume_m3"]),
                    bounds_min_m=tuple(record["bounds_min_m"]),
                    bounds_max_m=tuple(record["bounds_max_m"]),
                    pixel_count=int(record["pixel_count"]),
                )
                for record in metadata["portable_components"]
            ),
            occupancy_grid=arrays["occupancy_grid"],
            noise_sigma_m=arrays["noise_sigma_m"],
            intrinsics=arrays["intrinsics"],
            camera_to_shelf=arrays["camera_to_shelf"],
            calibration_checksum=metadata["calibration_checksum"],
            schema_version=metadata["schema_version"],
            approximate_metric=bool(metadata["approximate_metric"]),
            metadata=metadata.get("metadata", {}),
        )


@dataclass(slots=True)
class MidasAnchorAligner:
    """Affine alignment from MiDaS relative inverse-depth to metric depth.

    MiDaS remains an optional upstream inference step.  This adapter only accepts
    its relative inverse-depth output and known metric shelf anchors; it never
    downloads a model or pretends unaligned predictions are metric.
    """

    scale: float | None = None
    shift: float | None = None
    residual_m: float | None = None

    def fit(
        self,
        relative_inverse_depth: np.ndarray,
        anchors: Sequence[tuple[np.ndarray, float]],
        *,
        maximum_residual_m: float = 0.05,
    ) -> MidasAnchorAligner:
        if len(anchors) < 2:
            raise ValueError("at least two metric shelf-depth anchors are required")
        relative_values: list[float] = []
        metric_inverse_values: list[float] = []
        for mask, metric_depth_m in anchors:
            if metric_depth_m <= 0:
                raise ValueError("anchor depths must be positive")
            selected = np.asarray(relative_inverse_depth, dtype=np.float64)[
                np.asarray(mask, dtype=bool)
            ]
            selected = selected[np.isfinite(selected)]
            if not len(selected):
                raise ValueError("each anchor mask must contain a finite prediction")
            relative_values.append(float(np.median(selected)))
            metric_inverse_values.append(1.0 / metric_depth_m)
        design = np.column_stack((relative_values, np.ones(len(relative_values))))
        if np.linalg.matrix_rank(design) < 2:
            raise ValueError("anchor predictions do not span two distinct relative depths")
        scale, shift = np.linalg.lstsq(
            design, np.asarray(metric_inverse_values), rcond=None
        )[0]
        fitted_inverse = design @ np.array([scale, shift])
        fitted_depth = 1.0 / fitted_inverse
        metric_depth = 1.0 / np.asarray(metric_inverse_values)
        residual = float(np.sqrt(np.mean((fitted_depth - metric_depth) ** 2)))
        if not np.isfinite(residual) or residual > maximum_residual_m:
            raise ValueError(
                f"MiDaS anchor calibration residual {residual:.4f} m exceeds "
                f"{maximum_residual_m:.4f} m"
            )
        self.scale = float(scale)
        self.shift = float(shift)
        self.residual_m = residual
        return self

    def align(self, relative_inverse_depth: np.ndarray) -> np.ndarray:
        if self.scale is None or self.shift is None:
            raise RuntimeError("MiDaS anchor aligner has not been fitted")
        inverse_metric = (
            self.scale * np.asarray(relative_inverse_depth, dtype=np.float64) + self.shift
        )
        valid = np.isfinite(inverse_metric) & (inverse_metric > 1e-9)
        depth = np.zeros(inverse_metric.shape, dtype=np.float32)
        depth[valid] = (1.0 / inverse_metric[valid]).astype(np.float32)
        return depth

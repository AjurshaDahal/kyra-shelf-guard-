"""Frozen public data contracts shared by all four workstreams.

The runtime contracts use dataclasses because frames contain NumPy arrays. The
on-disk manifest uses Pydantic models in :mod:`kyra.manifest`.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

import numpy as np
import numpy.typing as npt

SCHEMA_VERSION = "1.0"
SHELF_CONFIG_C007_FIELDS = (
    "shelf_id",
    "roi_xyxy",
    "bounds_min_m",
    "bounds_max_m",
    "voxel_size_m",
)


class SourceType(StrEnum):
    SYNTHETIC_RGBD = "synthetic_rgbd"
    PUBLIC_RGBD = "public_rgbd"
    MIDAS_ALIGNED = "midas_aligned"


class ChangeType(StrEnum):
    REMOVAL = "REMOVAL"
    ADDITION = "ADDITION"
    UNKNOWN = "UNKNOWN"


class SystemMode(StrEnum):
    NORMAL = "NORMAL"
    RESTOCK_MODE = "RESTOCK_MODE"


def _array(
    value: npt.ArrayLike,
    dtype: npt.DTypeLike,
    *,
    ndim: int | None = None,
    shape: tuple[int, ...] | None = None,
) -> np.ndarray:
    result = np.asarray(value, dtype=dtype)
    if ndim is not None and result.ndim != ndim:
        raise ValueError(f"expected {ndim} dimensions, got shape {result.shape}")
    if shape is not None and result.shape != shape:
        raise ValueError(f"expected shape {shape}, got {result.shape}")
    return result


@dataclass(slots=True)
class ShelfConfig:
    shelf_id: str
    roi_xyxy: tuple[int, int, int, int]
    bounds_min_m: tuple[float, float, float]
    bounds_max_m: tuple[float, float, float]
    voxel_size_m: float = 0.01
    portable_max_volume_m3: float = 0.5
    removal_floor_m: float = 0.015
    registration_reject_m: float = 0.02
    minimum_visible_fraction: float = 0.70
    minimum_alert_volume_m3: float = 5e-5
    proximity_distance_m: float = 1.0

    @property
    def c007_fields(self) -> tuple[str, ...]:
        """Return the exact field names in the approved C-007 v1 shelf boundary."""
        return SHELF_CONFIG_C007_FIELDS

    @property
    def c007_values(self) -> dict[str, object]:
        """Return the approved C-007 v1 shelf boundary values without expanding scope."""
        return {name: getattr(self, name) for name in SHELF_CONFIG_C007_FIELDS}

    def __post_init__(self) -> None:
        x1, y1, x2, y2 = self.roi_xyxy
        if x2 <= x1 or y2 <= y1:
            raise ValueError("shelf ROI must have positive width and height")
        if any(
            high <= low
            for low, high in zip(
                self.bounds_min_m, self.bounds_max_m, strict=True
            )
        ):
            raise ValueError("shelf 3D bounds must have positive extent")
        if self.voxel_size_m <= 0:
            raise ValueError("voxel size must be positive")


@dataclass(slots=True)
class FramePacket:
    frame_id: str
    timestamp_ns: int
    rgb: np.ndarray
    depth_m: np.ndarray
    valid_depth_mask: np.ndarray
    intrinsics: np.ndarray
    camera_to_shelf: np.ndarray
    source_type: SourceType

    def __post_init__(self) -> None:
        self.rgb = _array(self.rgb, np.uint8, ndim=3)
        self.depth_m = _array(self.depth_m, np.float32, ndim=2)
        self.valid_depth_mask = _array(self.valid_depth_mask, bool, ndim=2)
        self.intrinsics = _array(self.intrinsics, np.float64, shape=(3, 3))
        self.camera_to_shelf = _array(self.camera_to_shelf, np.float64, shape=(4, 4))
        if self.rgb.shape[:2] != self.depth_m.shape:
            raise ValueError("RGB and depth dimensions differ")
        if self.valid_depth_mask.shape != self.depth_m.shape:
            raise ValueError("valid-depth mask and depth dimensions differ")
        # Invalid depth is always unknown, never free space.
        self.valid_depth_mask &= np.isfinite(self.depth_m) & (self.depth_m > 0)


@dataclass(slots=True, frozen=True)
class PortableComponent:
    component_id: str
    volume_m3: float
    bounds_min_m: tuple[float, float, float]
    bounds_max_m: tuple[float, float, float]
    pixel_count: int


@dataclass(slots=True)
class BaselineArtifact:
    shelf_id: str
    roi_xyxy: tuple[int, int, int, int]
    bounds_min_m: tuple[float, float, float]
    bounds_max_m: tuple[float, float, float]
    baseline_depth_m: np.ndarray
    valid_mask: np.ndarray
    fixed_geometry_mask: np.ndarray
    portable_components: tuple[PortableComponent, ...]
    occupancy_grid: np.ndarray
    noise_sigma_m: np.ndarray
    intrinsics: np.ndarray
    camera_to_shelf: np.ndarray
    calibration_checksum: str
    schema_version: str = SCHEMA_VERSION
    approximate_metric: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.baseline_depth_m = _array(self.baseline_depth_m, np.float32, ndim=2)
        self.valid_mask = _array(self.valid_mask, bool, ndim=2)
        self.fixed_geometry_mask = _array(self.fixed_geometry_mask, bool, ndim=2)
        self.noise_sigma_m = _array(self.noise_sigma_m, np.float32, ndim=2)
        self.occupancy_grid = _array(self.occupancy_grid, np.uint8, ndim=3)
        self.intrinsics = _array(self.intrinsics, np.float64, shape=(3, 3))
        self.camera_to_shelf = _array(self.camera_to_shelf, np.float64, shape=(4, 4))
        expected = self.baseline_depth_m.shape
        image_arrays = (
            self.valid_mask,
            self.fixed_geometry_mask,
            self.noise_sigma_m,
        )
        if any(array.shape != expected for array in image_arrays):
            raise ValueError("baseline image-space arrays must have identical dimensions")


@dataclass(slots=True)
class VolumeChangeEvent:
    event_id: str
    shelf_id: str
    change_type: ChangeType
    first_seen_timestamp_ns: int
    confirmation_timestamp_ns: int
    missing_volume_m3: float
    bounds_min_m: tuple[float, float, float]
    bounds_max_m: tuple[float, float, float]
    centroid_m: tuple[float, float, float]
    visible_shelf_fraction: float
    confidence: float
    rejection_reason: str | None = None
    evidence_frame_ids: tuple[str, ...] = ()


@dataclass(slots=True)
class PersonTrack:
    track_id: int
    timestamp_ns: int
    box_xyxy: tuple[float, float, float, float]
    pose_keypoints_xyc: np.ndarray
    position_m: tuple[float, float, float] | None
    near_shelf: bool
    wrist_in_shelf: bool = False
    authorized: bool = False
    last_near_timestamp_ns: int | None = None

    def __post_init__(self) -> None:
        self.pose_keypoints_xyc = _array(self.pose_keypoints_xyc, np.float32, ndim=2)
        if self.pose_keypoints_xyc.shape[1] != 3:
            raise ValueError("pose keypoints must have x, y, confidence columns")
        if self.near_shelf and self.last_near_timestamp_ns is None:
            self.last_near_timestamp_ns = self.timestamp_ns


@dataclass(slots=True, frozen=True)
class AlertEvent:
    alert_id: str
    shelf_id: str
    volume_event_id: str
    person_track_id: int
    rule_version: str
    first_seen_timestamp_ns: int
    alert_timestamp_ns: int
    missing_volume_m3: float
    confidence: float
    reason: str
    evidence_frame_ids: tuple[str, ...] = ()

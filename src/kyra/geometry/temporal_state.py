"""Temporal confirmation and baseline state tracking for Person 2."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass

import numpy as np

from kyra.contracts import (
    BaselineArtifact,
    ChangeType,
    FramePacket,
    ShelfConfig,
    VolumeChangeEvent,
)
from kyra.geometry.clustering import Cluster3D
from kyra.geometry.volume import VolumeEstimate

_MIN_PERSISTENCE_NS = 500_000_000  # 0.5 seconds
_RESTOCK_STABLE_NS = 2_000_000_000  # 2.0 seconds
_WINDOW_SIZE = 7
_MIN_POSITIVE_FRAMES = 5


@dataclass(slots=True)
class FrameObservation:
    timestamp_ns: int
    frame_id: str
    change_type: ChangeType
    volume_m3: float
    centroid_m: tuple[float, float, float]
    bounds_min_m: tuple[float, float, float]
    bounds_max_m: tuple[float, float, float]
    confidence: float
    visible_shelf_fraction: float
    is_occluded: bool


class TemporalChangeTracker:
    """Sliding-window temporal confirmation and deduplication engine.

    Requires:
      - Change detected in >= 5 of the latest 7 observations.
      - Temporal persistence >= 0.5 seconds (500 ms).
      - Shelf visibility >= minimum_visible_fraction (default 70%).
      - Volume >= minimum_alert_volume_m3 (default 5e-5 m^3).
    """

    def __init__(self, shelf_config: ShelfConfig) -> None:
        self.shelf_config = shelf_config
        self.history: deque[FrameObservation] = deque(maxlen=20)
        self.confirmed_active_event_id: str | None = None
        self.confirmed_change_type: ChangeType | None = None
        self.event_counter: int = 1

    def reset(self) -> None:
        self.history.clear()
        self.confirmed_active_event_id = None
        self.confirmed_change_type = None

    def process_frame(
        self,
        frame_id: str,
        timestamp_ns: int,
        change_type: ChangeType,
        cluster: Cluster3D | None,
        volume_estimate: VolumeEstimate | None,
        visible_shelf_fraction: float,
        is_occluded: bool,
    ) -> VolumeChangeEvent | None:
        """Process one frame observation and return a confirmed event if criteria are met."""
        vol = volume_estimate.volume_m3 if volume_estimate is not None else 0.0
        conf = volume_estimate.confidence if volume_estimate is not None else 0.0
        centroid = cluster.centroid_m if cluster is not None else (0.0, 0.0, 0.0)
        bounds_min = cluster.bounds_min_m if cluster is not None else (0.0, 0.0, 0.0)
        bounds_max = cluster.bounds_max_m if cluster is not None else (0.0, 0.0, 0.0)

        obs = FrameObservation(
            timestamp_ns=timestamp_ns,
            frame_id=frame_id,
            change_type=change_type,
            volume_m3=vol,
            centroid_m=centroid,
            bounds_min_m=bounds_min,
            bounds_max_m=bounds_max,
            confidence=conf,
            visible_shelf_fraction=visible_shelf_fraction,
            is_occluded=is_occluded,
        )
        self.history.append(obs)

        # Occlusion suppresses confirmation
        if is_occluded or visible_shelf_fraction < self.shelf_config.minimum_visible_fraction:
            return None

        # Look back at latest WINDOW_SIZE observations
        recent = list(self.history)[-_WINDOW_SIZE:]
        if len(recent) < _MIN_POSITIVE_FRAMES:
            return None

        # Check positive detections with same change type and volume >= min threshold
        target_type = change_type
        if target_type not in (ChangeType.REMOVAL, ChangeType.ADDITION):
            # No change or unknown -> clear active event if persistent
            no_change_count = sum(
                1
                for o in recent
                if o.change_type is ChangeType.UNKNOWN
                or o.volume_m3 < self.shelf_config.minimum_alert_volume_m3
            )
            if no_change_count >= _MIN_POSITIVE_FRAMES:
                self.confirmed_active_event_id = None
                self.confirmed_change_type = None
            return None

        matching = [
            o
            for o in recent
            if o.change_type is target_type
            and o.volume_m3 >= self.shelf_config.minimum_alert_volume_m3
            and not o.is_occluded
        ]

        if len(matching) < _MIN_POSITIVE_FRAMES:
            return None

        # Check temporal duration >= 0.5s
        first_seen = matching[0]
        last_seen = matching[-1]
        duration_ns = last_seen.timestamp_ns - first_seen.timestamp_ns
        if duration_ns < _MIN_PERSISTENCE_NS:
            return None

        # Deduplicate ongoing confirmed event
        if (
            self.confirmed_active_event_id is not None
            and self.confirmed_change_type is target_type
        ):
            return None  # Already confirmed and emitted

        # Create new confirmed event
        event_id = f"volume-event-{self.shelf_config.shelf_id}-{self.event_counter:04d}"
        self.event_counter += 1
        self.confirmed_active_event_id = event_id
        self.confirmed_change_type = target_type

        # Average metrics over matching observations
        avg_volume = float(np.mean([o.volume_m3 for o in matching]))
        avg_confidence = float(np.mean([o.confidence for o in matching]))
        avg_vis = float(np.mean([o.visible_shelf_fraction for o in matching]))
        evidence_frames = tuple(o.frame_id for o in matching)

        return VolumeChangeEvent(
            event_id=event_id,
            shelf_id=self.shelf_config.shelf_id,
            change_type=target_type,
            first_seen_timestamp_ns=first_seen.timestamp_ns,
            confirmation_timestamp_ns=last_seen.timestamp_ns,
            missing_volume_m3=avg_volume,
            bounds_min_m=last_seen.bounds_min_m,
            bounds_max_m=last_seen.bounds_max_m,
            centroid_m=last_seen.centroid_m,
            visible_shelf_fraction=avg_vis,
            confidence=avg_confidence,
            evidence_frame_ids=evidence_frames,
        )


def update_baseline_after_restock(
    baseline: BaselineArtifact,
    stable_frames: list[FramePacket],
    shelf_config: ShelfConfig,
) -> BaselineArtifact:
    """Update opening baseline artifact after verified authorized restocking.

    Requires at least 2.0 seconds of stable unobstructed observations.
    """
    if len(stable_frames) < 2:
        return baseline

    first_ts = stable_frames[0].timestamp_ns
    last_ts = stable_frames[-1].timestamp_ns
    if (last_ts - first_ts) < _RESTOCK_STABLE_NS:
        return baseline

    # Compute new median depth
    depth_stack = np.stack([f.depth_m for f in stable_frames], axis=0)
    valid_stack = np.stack([f.valid_depth_mask for f in stable_frames], axis=0)

    new_depth = np.median(depth_stack, axis=0).astype(np.float32)
    new_valid = np.all(valid_stack, axis=0)

    return BaselineArtifact(
        shelf_id=baseline.shelf_id,
        roi_xyxy=baseline.roi_xyxy,
        bounds_min_m=baseline.bounds_min_m,
        bounds_max_m=baseline.bounds_max_m,
        baseline_depth_m=new_depth,
        valid_mask=new_valid,
        fixed_geometry_mask=baseline.fixed_geometry_mask.copy(),
        portable_components=baseline.portable_components,
        occupancy_grid=baseline.occupancy_grid.copy(),
        noise_sigma_m=baseline.noise_sigma_m.copy(),
        intrinsics=baseline.intrinsics.copy(),
        camera_to_shelf=baseline.camera_to_shelf.copy(),
        calibration_checksum=baseline.calibration_checksum,
        schema_version=baseline.schema_version,
        approximate_metric=baseline.approximate_metric,
        metadata={**baseline.metadata, "restocked_at_ns": last_ts},
    )

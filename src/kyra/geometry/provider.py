"""ShelfGeometryProvider implementing the frozen GeometryProvider protocol."""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np

from kyra.contracts import (
    BaselineArtifact,
    ChangeType,
    FramePacket,
    ShelfConfig,
    VolumeChangeEvent,
)
from kyra.differencing.signed_diff import compute_signed_depth_difference
from kyra.geometry.clustering import extract_3d_clusters
from kyra.geometry.registration import register_frame_to_baseline
from kyra.geometry.temporal_state import TemporalChangeTracker
from kyra.geometry.volume import estimate_cluster_volume
from kyra.occlusion.safety import evaluate_occlusion_safety


class ShelfGeometryProvider:
    """Production Person 2 geometry provider implementing the GeometryProvider protocol.

    Orchestrates:
      1. Shelf registration and drift check.
      2. Occlusion safety and shelf visibility assessment.
      3. Signed depth differencing with M3C2-EP 3σ noise thresholding.
      4. 3D spatial clustering and frustum ray volume estimation.
      5. Sliding-window temporal persistence confirmation and event deduplication.
    """

    def __init__(self) -> None:
        self._trackers: dict[str, TemporalChangeTracker] = {}

    def _get_tracker(self, shelf_config: ShelfConfig) -> TemporalChangeTracker:
        if shelf_config.shelf_id not in self._trackers:
            self._trackers[shelf_config.shelf_id] = TemporalChangeTracker(shelf_config)
        return self._trackers[shelf_config.shelf_id]

    def reset(self, shelf_id: str | None = None) -> None:
        if shelf_id is None:
            self._trackers.clear()
        elif shelf_id in self._trackers:
            self._trackers[shelf_id].reset()

    def __call__(
        self,
        baseline: BaselineArtifact,
        frames: Sequence[FramePacket],
        shelf_config: ShelfConfig,
    ) -> tuple[VolumeChangeEvent, ...]:
        return self.detect_changes(baseline, frames, shelf_config)

    def detect_changes(
        self,
        baseline: BaselineArtifact,
        frames: Sequence[FramePacket],
        shelf_config: ShelfConfig,
        *,
        person_occlusion_masks: Sequence[np.ndarray | None] | None = None,
    ) -> tuple[VolumeChangeEvent, ...]:
        """Process sequence of observation frames and detect confirmed volume change events."""
        if not frames:
            return ()

        tracker = self._get_tracker(shelf_config)
        confirmed_events: list[VolumeChangeEvent] = []

        for idx, frame in enumerate(frames):
            person_mask = (
                person_occlusion_masks[idx]
                if person_occlusion_masks is not None and idx < len(person_occlusion_masks)
                else None
            )

            # Step 1: Shelf registration and drift check
            reg_result = register_frame_to_baseline(frame, baseline, shelf_config)
            if reg_result.rejected:
                # Frame rejected due to drift envelope or high residual
                event = tracker.process_frame(
                    frame_id=frame.frame_id,
                    timestamp_ns=frame.timestamp_ns,
                    change_type=ChangeType.UNKNOWN,
                    cluster=None,
                    volume_estimate=None,
                    visible_shelf_fraction=0.0,
                    is_occluded=True,
                )
                if event is not None:
                    confirmed_events.append(event)
                continue

            working_depth = (
                reg_result.corrected_depth_m
                if reg_result.corrected_depth_m is not None
                else frame.depth_m
            )

            # Step 2: Occlusion safety
            occ_result = evaluate_occlusion_safety(
                frame, baseline, shelf_config, person_occlusion_mask=person_mask
            )

            # Step 3: Signed depth differencing with 3σ thresholding
            diff_result = compute_signed_depth_difference(
                working_depth,
                baseline,
                shelf_config,
                frame.valid_depth_mask,
                person_occlusion_mask=person_mask,
            )

            # Step 3b: Paired removal+addition drift detection (Issue #79).
            # Camera drift shifts the image horizontally, creating a paired
            # pattern: the object's old position exposes the wall (false
            # removal) while its new position occludes the wall (addition).
            # When both removal and addition pixel counts are significant and
            # comparable, suppress the change as UNKNOWN drift artifact.
            _drift_suppressed = False
            if (
                diff_result.removal_pixel_count > 0
                and diff_result.addition_pixel_count > 0
            ):
                _r = diff_result.removal_pixel_count
                _a = diff_result.addition_pixel_count
                _ratio = min(_r, _a) / max(_r, _a) if max(_r, _a) > 0 else 0.0
                if _ratio >= 0.3:
                    # Comparable removal and addition — drift signature.
                    _drift_suppressed = True

            # Step 4: 3D clustering and metric volume
            change_type = ChangeType.UNKNOWN
            best_cluster = None
            vol_estimate = None

            if _drift_suppressed:
                pass  # Suppress as drift artifact — treat as UNKNOWN
            elif diff_result.removal_pixel_count > 0:
                clusters = extract_3d_clusters(
                    diff_result.removal_candidate_mask,
                    working_depth,
                    frame.intrinsics,
                    frame.camera_to_shelf,
                )
                if clusters:
                    best_cluster = clusters[0]
                    vol_estimate = estimate_cluster_volume(
                        best_cluster,
                        working_depth,
                        baseline.baseline_depth_m,
                        frame.intrinsics,
                        shelf_config,
                        baseline_occupancy_grid=baseline.occupancy_grid,
                    )
                    change_type = ChangeType.REMOVAL
            elif diff_result.addition_pixel_count > 0:
                clusters = extract_3d_clusters(
                    diff_result.addition_candidate_mask,
                    working_depth,
                    frame.intrinsics,
                    frame.camera_to_shelf,
                )
                if clusters:
                    best_cluster = clusters[0]
                    vol_estimate = estimate_cluster_volume(
                        best_cluster,
                        working_depth,
                        baseline.baseline_depth_m,
                        frame.intrinsics,
                        shelf_config,
                        baseline_occupancy_grid=baseline.occupancy_grid,
                    )
                    change_type = ChangeType.ADDITION

            # Step 5: Temporal state confirmation
            event = tracker.process_frame(
                frame_id=frame.frame_id,
                timestamp_ns=frame.timestamp_ns,
                change_type=change_type,
                cluster=best_cluster,
                volume_estimate=vol_estimate,
                visible_shelf_fraction=occ_result.visible_shelf_fraction,
                is_occluded=occ_result.is_occluded,
            )
            if event is not None:
                confirmed_events.append(event)

        return tuple(confirmed_events)

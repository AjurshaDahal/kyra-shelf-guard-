from __future__ import annotations

import numpy as np

from kyra.contracts import PersonTrack
from kyra.io import ScenarioFrameSource


class ReplayTracker:
    """Convert saved scenario track annotations into PersonTrack objects."""

    def __init__(self, source: ScenarioFrameSource) -> None:
        self.source = source

    def tracks_for_frame(
        self,
        frame_id: str,
    ) -> tuple[PersonTrack, ...]:
        """Return deterministic PersonTrack objects for one replay frame."""

        frame = self.source.get(frame_id)
        annotations = self.source.track_annotations(frame_id)

        return tuple(
            PersonTrack(
                track_id=annotation.track_id,
                timestamp_ns=frame.timestamp_ns,
                box_xyxy=annotation.box_xyxy,
                pose_keypoints_xyc=(
                    annotation.pose_keypoints_xyc
                    if annotation.pose_keypoints_xyc
                    else np.empty((0, 3), dtype=np.float32)
                ),
                position_m=None,
                near_shelf=False,
                wrist_in_shelf=False,
                authorized=annotation.authorized,
                last_near_timestamp_ns=None,
            )
            for annotation in annotations
        )

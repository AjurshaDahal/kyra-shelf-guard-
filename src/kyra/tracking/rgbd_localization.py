"""Metric RGB-D localization for pretrained person tracks."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import replace

import numpy as np

from kyra.contracts import FramePacket, PersonTrack, ShelfConfig
from kyra.geometry.points import transform_points
from kyra.proximity.person_proximity import update_proximity


def _track_position_from_depth(
    track: PersonTrack,
    frame: FramePacket,
    *,
    minimum_valid_samples: int,
) -> tuple[float, float, float] | None:
    """Estimate one shelf-frame position from the inner person-box depth."""

    height, width = frame.depth_m.shape
    left, top, right, bottom = track.box_xyxy
    if not all(np.isfinite((left, top, right, bottom))):
        return None

    # Sample the inner torso/lower-body region to limit shelf-background pixels
    # and exclude the least stable box edges. Bounds stay half-open.
    box_width = right - left
    box_height = bottom - top
    if box_width <= 0 or box_height <= 0:
        return None
    sample_left = max(0, int(np.floor(left + 0.25 * box_width)))
    sample_right = min(width, int(np.ceil(left + 0.75 * box_width)))
    sample_top = max(0, int(np.floor(top + 0.35 * box_height)))
    sample_bottom = min(height, int(np.ceil(top + 0.85 * box_height)))
    if sample_right <= sample_left or sample_bottom <= sample_top:
        return None

    valid = frame.valid_depth_mask[sample_top:sample_bottom, sample_left:sample_right]
    depth = frame.depth_m[sample_top:sample_bottom, sample_left:sample_right]
    samples = depth[valid & np.isfinite(depth) & (depth > 0)]
    if samples.size < minimum_valid_samples:
        return None

    z_m = float(np.median(samples))
    intrinsics = frame.intrinsics
    fx = float(intrinsics[0, 0])
    fy = float(intrinsics[1, 1])
    if not np.isfinite((fx, fy)).all() or fx <= 0 or fy <= 0:
        return None

    # The depth is robustly sampled from the inner region; use that region's
    # centre as the associated image coordinate for metric back-projection.
    u = (sample_left + sample_right - 1) / 2.0
    v = (sample_top + sample_bottom - 1) / 2.0
    cx = float(intrinsics[0, 2])
    cy = float(intrinsics[1, 2])
    camera_point = np.array(
        [[(u - cx) * z_m / fx, (v - cy) * z_m / fy, z_m]],
        dtype=np.float64,
    )
    shelf_point = transform_points(camera_point, frame.camera_to_shelf)[0]
    if not np.isfinite(shelf_point).all():
        return None
    return tuple(float(value) for value in shelf_point)


def localize_tracks_from_rgbd(
    tracks: Sequence[PersonTrack],
    frames: Sequence[FramePacket],
    shelf: ShelfConfig,
    *,
    minimum_valid_samples: int = 9,
) -> tuple[PersonTrack, ...]:
    """Return copied tracks with metric position and proximity when observable.

    Unknown or insufficient depth produces ``position_m=None`` and
    ``near_shelf=False``. Prior ``last_near_timestamp_ns`` state is retained for
    a continuing track, allowing the existing two-second rule to associate a
    removal that becomes visible shortly after a person's occlusion clears.
    """

    if minimum_valid_samples < 1:
        raise ValueError("minimum_valid_samples must be positive")

    frames_by_timestamp = {frame.timestamp_ns: frame for frame in frames}
    if len(frames_by_timestamp) != len(frames):
        raise ValueError("RGB-D frame timestamps must be unique")

    previous_by_id: dict[int, PersonTrack] = {}
    localized: list[PersonTrack] = []
    for track in tracks:
        try:
            frame = frames_by_timestamp[track.timestamp_ns]
        except KeyError as exc:
            raise ValueError(
                f"no RGB-D frame matches track timestamp {track.timestamp_ns}"
            ) from exc

        previous = previous_by_id.get(track.track_id)
        last_near = (
            track.last_near_timestamp_ns
            if track.last_near_timestamp_ns is not None
            else previous.last_near_timestamp_ns
            if previous is not None
            else None
        )
        positioned = replace(
            track,
            position_m=_track_position_from_depth(
                track,
                frame,
                minimum_valid_samples=minimum_valid_samples,
            ),
            near_shelf=False,
            last_near_timestamp_ns=last_near,
        )
        update_proximity(positioned, shelf)
        previous_by_id[positioned.track_id] = positioned
        localized.append(positioned)

    return tuple(localized)

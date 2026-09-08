from __future__ import annotations

import numpy as np
import pytest

from kyra.contracts import PersonTrack, ShelfConfig
from kyra.tracking.rgbd_localization import localize_tracks_from_rgbd


def _shelf(*, proximity_distance_m: float = 0.25) -> ShelfConfig:
    return ShelfConfig(
        shelf_id="shelf-localization",
        roi_xyxy=(0, 0, 12, 12),
        bounds_min_m=(-0.5, -0.5, 1.5),
        bounds_max_m=(0.5, 0.5, 2.5),
        proximity_distance_m=proximity_distance_m,
    )


def _track(timestamp_ns: int = 1_000_000_000) -> PersonTrack:
    return PersonTrack(
        track_id=7,
        timestamp_ns=timestamp_ns,
        box_xyxy=(2.0, 1.0, 10.0, 11.0),
        pose_keypoints_xyc=np.empty((0, 3), dtype=np.float32),
        position_m=None,
        near_shelf=False,
    )


def test_localizes_metric_depth_and_updates_proximity(make_frame_packet) -> None:
    depth = np.full((12, 12), 2.0, dtype=np.float32)
    intrinsics = np.array(
        [[10.0, 0.0, 5.5], [0.0, 10.0, 5.5], [0.0, 0.0, 1.0]],
        dtype=np.float64,
    )
    frame = make_frame_packet(depth_m=depth)
    frame.intrinsics = intrinsics

    (localized,) = localize_tracks_from_rgbd((_track(),), (frame,), _shelf())

    assert localized.position_m == pytest.approx((0.0, 0.2, 2.0))
    assert localized.near_shelf is True
    assert localized.last_near_timestamp_ns == localized.timestamp_ns


def test_applies_camera_to_shelf_transform(make_frame_packet) -> None:
    depth = np.full((12, 12), 2.0, dtype=np.float32)
    transform = np.eye(4, dtype=np.float64)
    transform[0, 3] = 3.0
    frame = make_frame_packet(depth_m=depth)
    frame.camera_to_shelf = transform

    (localized,) = localize_tracks_from_rgbd((_track(),), (frame,), _shelf())

    assert localized.position_m is not None
    assert localized.position_m[0] > 2.0
    assert localized.near_shelf is False


def test_unknown_depth_fails_closed(make_frame_packet) -> None:
    depth = np.full((12, 12), 2.0, dtype=np.float32)
    valid = np.zeros((12, 12), dtype=bool)
    frame = make_frame_packet(depth_m=depth, valid_depth_mask=valid)

    (localized,) = localize_tracks_from_rgbd((_track(),), (frame,), _shelf())

    assert localized.position_m is None
    assert localized.near_shelf is False
    assert localized.last_near_timestamp_ns is None


def test_inner_box_sample_ignores_background_edges(make_frame_packet) -> None:
    depth = np.full((12, 12), 8.0, dtype=np.float32)
    depth[4:10, 4:8] = 2.0
    frame = make_frame_packet(depth_m=depth)

    (localized,) = localize_tracks_from_rgbd((_track(),), (frame,), _shelf())

    assert localized.position_m is not None
    assert localized.position_m[2] == pytest.approx(2.0)


def test_continuing_track_preserves_last_near_time_when_depth_disappears(
    make_frame_packet,
) -> None:
    first = make_frame_packet(depth_m=np.full((12, 12), 2.0, dtype=np.float32))
    second = make_frame_packet(
        frame_id="frame-0002",
        timestamp_ns=2_000_000_000,
        depth_m=np.zeros((12, 12), dtype=np.float32),
    )

    first_track = _track(first.timestamp_ns)
    second_track = _track(second.timestamp_ns)
    localized = localize_tracks_from_rgbd(
        (first_track, second_track),
        (first, second),
        _shelf(),
    )

    assert localized[0].near_shelf is True
    assert localized[1].near_shelf is False
    assert localized[1].position_m is None
    assert localized[1].last_near_timestamp_ns == first.timestamp_ns


def test_rejects_track_without_matching_frame(make_frame_packet) -> None:
    with pytest.raises(ValueError, match="no RGB-D frame matches"):
        localize_tracks_from_rgbd((_track(99),), (make_frame_packet(),), _shelf())

from __future__ import annotations

import numpy as np
import pytest

from kyra.contracts import PersonTrack


def make_person_track() -> PersonTrack:
    return PersonTrack(
        track_id=17,
        timestamp_ns=2_000_000_000,
        box_xyxy=(10.0, 20.0, 50.0, 90.0),
        pose_keypoints_xyc=np.array(
            [[20.0, 30.0, 0.95], [40.0, 70.0, 0.85]],
            dtype=np.float64,
        ),
        position_m=(0.1, 0.2, 0.8),
        near_shelf=True,
        wrist_in_shelf=True,
        authorized=False,
    )


def test_person_track_compatibility_fixture_preserves_contract_values() -> None:
    track = make_person_track()

    assert track.track_id == 17
    assert track.timestamp_ns == 2_000_000_000
    assert track.box_xyxy == (10.0, 20.0, 50.0, 90.0)
    assert track.position_m == (0.1, 0.2, 0.8)
    assert track.near_shelf
    assert track.wrist_in_shelf
    assert not track.authorized
    assert track.last_near_timestamp_ns == track.timestamp_ns
    assert track.pose_keypoints_xyc.shape == (2, 3)
    assert track.pose_keypoints_xyc.dtype == np.float32
    np.testing.assert_allclose(
        track.pose_keypoints_xyc,
        np.array([[20.0, 30.0, 0.95], [40.0, 70.0, 0.85]], dtype=np.float32),
    )


def test_person_track_preserves_explicit_last_near_timestamp() -> None:
    track = make_person_track()
    track.last_near_timestamp_ns = 1_500_000_000

    assert track.last_near_timestamp_ns == 1_500_000_000


def test_person_track_rejects_pose_keypoints_without_three_columns() -> None:
    with pytest.raises(ValueError, match="x, y, confidence columns"):
        PersonTrack(
            track_id=17,
            timestamp_ns=2_000_000_000,
            box_xyxy=(10.0, 20.0, 50.0, 90.0),
            pose_keypoints_xyc=np.zeros((2, 2), dtype=np.float32),
            position_m=None,
            near_shelf=False,
        )


def test_person_track_not_near_shelf_does_not_invent_near_timestamp() -> None:
    track = PersonTrack(
        track_id=17,
        timestamp_ns=2_000_000_000,
        box_xyxy=(10.0, 20.0, 50.0, 90.0),
        pose_keypoints_xyc=np.empty((0, 3), dtype=np.float32),
        position_m=None,
        near_shelf=False,
    )

    assert track.last_near_timestamp_ns is None

from kyra.contracts import PersonTrack
from kyra.proximity.person_proximity import (
    is_person_near_shelf,
    update_proximity,
)


def make_track(
    position_m: tuple[float, float, float] | None,
    timestamp_ns: int = 2_000_000_000,
) -> PersonTrack:
    return PersonTrack(
        track_id=7,
        timestamp_ns=timestamp_ns,
        box_xyxy=(1.0, 0.0, 4.0, 3.0),
        pose_keypoints_xyc=[
            (1.0, 1.0, 0.9),
            (3.0, 2.0, 0.8),
        ],
        position_m=position_m,
        near_shelf=False,
    )


def test_person_inside_shelf_bounds_is_near(shelf_config):
    track = make_track((0.0, 0.0, 0.8))

    assert is_person_near_shelf(track, shelf_config)


def test_person_far_from_shelf_is_not_near(shelf_config):
    track = make_track((5.0, 5.0, 5.0))

    assert not is_person_near_shelf(track, shelf_config)


def test_missing_position_is_not_near(shelf_config):
    track = make_track(None)

    assert not is_person_near_shelf(track, shelf_config)


def test_update_proximity_records_near_timestamp(shelf_config):
    track = make_track((0.0, 0.0, 0.8))

    update_proximity(track, shelf_config)

    assert track.near_shelf
    assert track.last_near_timestamp_ns == 2_000_000_000

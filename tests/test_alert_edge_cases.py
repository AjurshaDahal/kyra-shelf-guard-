from kyra.contracts import ChangeType, PersonTrack, VolumeChangeEvent
from kyra.proximity.person_proximity import update_proximity
from kyra.rules.alert_engine import evaluate_removal_alert


def make_track(
    *,
    track_id: int = 7,
    position_m: tuple[float, float, float] | None = (0.1, 0.0, 0.8),
    timestamp_ns: int = 2_000_000_000,
    authorized: bool = False,
) -> PersonTrack:
    return PersonTrack(
        track_id=track_id,
        timestamp_ns=timestamp_ns,
        box_xyxy=(1.0, 0.0, 4.0, 3.0),
        pose_keypoints_xyc=[
            (1.0, 1.0, 0.9),
            (3.0, 2.0, 0.8),
        ],
        position_m=position_m,
        near_shelf=False,
        authorized=authorized,
        last_near_timestamp_ns=None,
    )


def make_removal_event(
    *,
    timestamp_ns: int = 2_000_000_000,
) -> VolumeChangeEvent:
    return VolumeChangeEvent(
        event_id="volume-edge-001",
        shelf_id="shelf-01",
        change_type=ChangeType.REMOVAL,
        first_seen_timestamp_ns=timestamp_ns,
        confirmation_timestamp_ns=timestamp_ns + 500_000_000,
        missing_volume_m3=0.0025,
        bounds_min_m=(0.0, 0.0, 0.0),
        bounds_max_m=(0.1, 0.1, 0.1),
        centroid_m=(0.05, 0.05, 0.05),
        visible_shelf_fraction=0.95,
        confidence=0.9,
        evidence_frame_ids=("frame-0002",),
    )


def test_person_exactly_on_shelf_boundary_is_near(shelf_config):
    track = make_track(position_m=shelf_config.bounds_max_m)

    updated = update_proximity(track, shelf_config)

    assert updated.near_shelf is True
    assert updated.last_near_timestamp_ns == track.timestamp_ns


def test_person_with_no_position_is_not_near(shelf_config):
    track = make_track(position_m=None)

    updated = update_proximity(track, shelf_config)

    assert updated.near_shelf is False
    assert updated.last_near_timestamp_ns is None


def test_person_far_away_does_not_get_near_timestamp(shelf_config):
    track = make_track(position_m=(100.0, 100.0, 100.0))

    updated = update_proximity(track, shelf_config)

    assert updated.near_shelf is False
    assert updated.last_near_timestamp_ns is None


def test_alert_uses_most_recent_eligible_person(shelf_config):
    event = make_removal_event()

    older = make_track(
        track_id=1,
        timestamp_ns=2_000_000_000,
    )
    older.last_near_timestamp_ns = 1_000_000_000

    newer = make_track(
        track_id=2,
        timestamp_ns=2_000_000_000,
    )
    newer.last_near_timestamp_ns = 1_500_000_000

    alert = evaluate_removal_alert(
        event,
        (older, newer),
        shelf_config,
    )

    assert alert is not None
    assert alert.person_track_id == 2

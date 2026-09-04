from kyra.contracts import (
    ChangeType,
    PersonTrack,
    SystemMode,
    VolumeChangeEvent,
)
from kyra.rules.alert_engine import evaluate_removal_alert


def make_track(
    *,
    track_id: int = 7,
    timestamp_ns: int = 2_000_000_000,
    last_near_timestamp_ns: int | None = 1_000_000_000,
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
        position_m=(0.1, 0.0, 0.8),
        near_shelf=True,
        authorized=authorized,
        last_near_timestamp_ns=last_near_timestamp_ns,
    )


def make_removal_event(
    *,
    timestamp_ns: int = 2_000_000_000,
    volume_m3: float = 0.0025,
) -> VolumeChangeEvent:
    return VolumeChangeEvent(
        event_id="volume-001",
        shelf_id="shelf-01",
        change_type=ChangeType.REMOVAL,
        first_seen_timestamp_ns=timestamp_ns,
        confirmation_timestamp_ns=timestamp_ns + 500_000_000,
        missing_volume_m3=volume_m3,
        bounds_min_m=(0.0, 0.0, 0.0),
        bounds_max_m=(0.1, 0.1, 0.1),
        centroid_m=(0.05, 0.05, 0.05),
        visible_shelf_fraction=0.95,
        confidence=0.9,
        evidence_frame_ids=("frame-0002",),
    )


def test_removal_near_non_authorized_person_creates_alert(shelf_config):
    event = make_removal_event()
    track = make_track()

    alert = evaluate_removal_alert(
        event,
        (track,),
        shelf_config,
    )

    assert alert is not None
    assert alert.person_track_id == 7
    assert alert.volume_event_id == "volume-001"
    assert alert.shelf_id == "shelf-01"


def test_authorized_person_does_not_create_alert(shelf_config):
    event = make_removal_event()
    track = make_track(authorized=True)

    alert = evaluate_removal_alert(
        event,
        (track,),
        shelf_config,
    )

    assert alert is None


def test_person_outside_two_second_window_does_not_alert(shelf_config):
    event = make_removal_event(timestamp_ns=4_000_000_000)
    track = make_track(last_near_timestamp_ns=1_000_000_000)

    alert = evaluate_removal_alert(
        event,
        (track,),
        shelf_config,
    )

    assert alert is None


def test_small_missing_volume_does_not_alert(shelf_config):
    event = make_removal_event(
        volume_m3=shelf_config.minimum_alert_volume_m3 / 2,
    )
    track = make_track()

    alert = evaluate_removal_alert(
        event,
        (track,),
        shelf_config,
    )

    assert alert is None


def test_addition_does_not_create_removal_alert(shelf_config):
    event = make_removal_event()
    event.change_type = ChangeType.ADDITION
    track = make_track()

    alert = evaluate_removal_alert(
        event,
        (track,),
        shelf_config,
    )

    assert alert is None


def test_restock_mode_suppresses_alert(shelf_config):
    event = make_removal_event()
    track = make_track()

    alert = evaluate_removal_alert(
        event,
        (track,),
        shelf_config,
        system_mode=SystemMode.RESTOCK_MODE,
    )

    assert alert is None

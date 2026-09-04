from kyra.contracts import ChangeType, VolumeChangeEvent
from kyra.io import ScenarioFrameSource
from kyra.proximity.person_proximity import update_proximity
from kyra.rules.alert_engine import evaluate_removal_alert
from kyra.tracking.replay_tracker import ReplayTracker


def test_person3_pipeline_creates_alert(scenario_path, shelf_config):
    source = ScenarioFrameSource(scenario_path)
    tracker = ReplayTracker(source)

    # 1. Reconstruct the saved person track.
    tracks = tracker.tracks_for_frame("frame-0002")

    assert len(tracks) == 1
    assert tracks[0].track_id == 7

    # 2. Simulate the 3D position supplied by the depth/3D stage.
    tracks[0].position_m = (0.1, 0.0, 0.8)

    # 3. Calculate/update shelf proximity.
    tracks = tuple(
        update_proximity(
            track,
            shelf_config,
        )
        for track in tracks
    )

    assert tracks[0].near_shelf is True
    assert tracks[0].last_near_timestamp_ns == 2_000_000_000

    # 4. Simulate the volume-removal event from Person 1/2.
    event = VolumeChangeEvent(
        event_id="volume-001",
        shelf_id="shelf-01",
        change_type=ChangeType.REMOVAL,
        first_seen_timestamp_ns=2_000_000_000,
        confirmation_timestamp_ns=2_500_000_000,
        missing_volume_m3=0.0025,
        bounds_min_m=(0.0, 0.0, 0.0),
        bounds_max_m=(0.1, 0.1, 0.1),
        centroid_m=(0.05, 0.05, 0.05),
        visible_shelf_fraction=0.95,
        confidence=0.9,
        evidence_frame_ids=("frame-0002",),
    )

    # 5. Evaluate the suspicious shelf-removal rule.
    alert = evaluate_removal_alert(
        event,
        tracks,
        shelf_config,
    )

    assert alert is not None
    assert alert.person_track_id == 7
    assert alert.volume_event_id == "volume-001"
    assert alert.shelf_id == "shelf-01"

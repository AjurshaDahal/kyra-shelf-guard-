from kyra.io import ScenarioFrameSource
from kyra.manifest import load_manifest, write_manifest
from kyra.tracking.replay_tracker import ReplayTracker


def test_replay_tracker_reconstructs_person_track(scenario_path):
    manifest = load_manifest(scenario_path)
    manifest.frames[1].tracks[0].pose_keypoints_xyc = [
        (1.0, 1.0, 0.9),
        (3.0, 2.0, 0.8),
    ]
    write_manifest(manifest, scenario_path)

    source = ScenarioFrameSource(scenario_path)
    tracker = ReplayTracker(source)

    tracks = tracker.tracks_for_frame("frame-0002")

    assert len(tracks) == 1

    track = tracks[0]

    assert track.track_id == 7
    assert track.timestamp_ns == 2_000_000_000
    assert track.box_xyxy == (1.0, 0.0, 4.0, 3.0)
    assert track.pose_keypoints_xyc.shape == (2, 3)
    assert track.authorized is False
    assert track.near_shelf is False
    assert track.position_m is None


def test_replay_tracker_is_deterministic(scenario_path):
    source = ScenarioFrameSource(scenario_path)
    tracker = ReplayTracker(source)

    first = tracker.tracks_for_frame("frame-0002")
    second = tracker.tracks_for_frame("frame-0002")

    assert len(first) == len(second)

    assert first[0].track_id == second[0].track_id
    assert first[0].timestamp_ns == second[0].timestamp_ns
    assert first[0].box_xyxy == second[0].box_xyxy

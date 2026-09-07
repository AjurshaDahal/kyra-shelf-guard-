"""Demo orchestration pipeline."""

from pathlib import Path
from typing import Any

from kyra.baseline import BaselineBuilder
from kyra.contracts import AlertEvent, ShelfConfig, SystemMode, VolumeChangeEvent
from kyra.differencing.signed_diff import compute_signed_depth_difference
from kyra.geometry.provider import ShelfGeometryProvider
from kyra.geometry.registration import register_frame_to_baseline
from kyra.io import ScenarioFrameSource
from kyra.proximity.occlusion import build_person_occlusion_mask
from kyra.proximity.person_proximity import update_proximity
from kyra.rules.alert_engine import evaluate_removal_alert
from kyra.tracking.replay_tracker import ReplayTracker
from kyra.viz.annotate import annotate_frame
from kyra.viz.video import create_demo_video


def run_demo_scenario(manifest_path: str | Path, output_video_path: str | Path) -> dict[str, Any]:
    """Run the pipeline and generate an annotated demo video."""
    source = ScenarioFrameSource(manifest_path)
    shelf = ShelfConfig(**source.manifest.shelf.c007_values)

    baseline = BaselineBuilder(minimum_frames=len(source.manifest.baseline_frame_ids)).fit(
        source.baseline_frames(), shelf
    )

    tracker = ReplayTracker(source)
    event_frames = list(source.event_frames())

    provider = ShelfGeometryProvider()
    mode = SystemMode(source.manifest.system_mode)

    annotated_frames = []

    # State tracking for alerts
    active_events: list[VolumeChangeEvent] = []
    active_alerts: list[AlertEvent] = []
    alerted_event_ids: set[str] = set()
    track_state = {}

    for frame in event_frames:
        # Tracking
        tracks = list(tracker.tracks_for_frame(frame.frame_id))
        annotations = source.track_annotations(frame.frame_id)

        track_boxes = []
        for track, annotation in zip(tracks, annotations, strict=True):
            previous = track_state.get(track.track_id)
            if previous is not None:
                track.last_near_timestamp_ns = previous.last_near_timestamp_ns
            track.position_m = annotation.position_m
            track.authorized = annotation.authorized
            update_proximity(track, shelf)
            track_state[track.track_id] = track

            if hasattr(annotation, "box_xyxy") and annotation.box_xyxy is not None:
                track_boxes.append((track.track_id, annotation.box_xyxy, track.authorized))

        replay_mask = build_person_occlusion_mask(tuple(tracks), frame.depth_m.shape)
        person_mask = source.occlusion_mask(frame.frame_id) | replay_mask

        # For viz, get the diff result manually
        reg_result = register_frame_to_baseline(frame, baseline, shelf)
        working_depth = (
            reg_result.corrected_depth_m
            if reg_result.corrected_depth_m is not None
            else frame.depth_m
        )
        diff_result = compute_signed_depth_difference(
            working_depth,
            baseline,
            shelf,
            frame.valid_depth_mask,
            person_occlusion_mask=person_mask,
        )

        # Run the real provider logic on this single frame to update state
        events = provider.detect_changes(
            baseline, [frame], shelf, person_occlusion_masks=[person_mask]
        )
        if events:
            active_events.extend(events)

        for event in events:
            if event.event_id in alerted_event_ids:
                continue
            alert = evaluate_removal_alert(
                event,
                tuple(track_state.values()),
                shelf,
                system_mode=mode,
            )
            if alert is not None:
                active_alerts.append(alert)
                alerted_event_ids.add(event.event_id)

        # Annotate
        composite = annotate_frame(
            frame=frame,
            shelf_config=shelf,
            diff_result=diff_result,
            events=active_events,
            alerts=active_alerts,
            person_mask=person_mask,
            track_boxes=track_boxes,
        )
        annotated_frames.append(composite)

    create_demo_video(annotated_frames, output_video_path, fps=5.0)

    return {
        "manifest_path": str(Path(manifest_path).resolve()),
        "output_video": str(Path(output_video_path).resolve()),
        "frames_processed": len(event_frames),
        "events_detected": len(active_events),
        "alerts_triggered": len(active_alerts),
    }

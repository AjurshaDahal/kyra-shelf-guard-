"""Deterministic alert rules for Person 3."""

from __future__ import annotations

from kyra.contracts import (
    AlertEvent,
    ChangeType,
    PersonTrack,
    ShelfConfig,
    SystemMode,
    VolumeChangeEvent,
)

RULE_VERSION = "P3-001"
ASSOCIATION_WINDOW_NS = 2_000_000_000


def evaluate_removal_alert(
    volume_event: VolumeChangeEvent,
    tracks: tuple[PersonTrack, ...],
    shelf: ShelfConfig,
    system_mode: SystemMode = SystemMode.NORMAL,
) -> AlertEvent | None:
    """Evaluate whether a volume-removal event should produce an alert."""

    # Only confirmed removals can produce a removal alert.
    if volume_event.change_type is not ChangeType.REMOVAL:
        return None

    # Ignore events whose missing volume is below the configured threshold.
    if volume_event.missing_volume_m3 < shelf.minimum_alert_volume_m3:
        return None

    # Never alert while the system is explicitly in restock mode.
    if system_mode is SystemMode.RESTOCK_MODE:
        return None

    candidate: PersonTrack | None = None

    for track in tracks:
        if track.authorized:
            continue

        if track.last_near_timestamp_ns is None:
            continue

        # Person must have been near the shelf no more than two seconds
        # before the removal was first observed.
        delta_ns = volume_event.first_seen_timestamp_ns - track.last_near_timestamp_ns

        if 0 <= delta_ns <= ASSOCIATION_WINDOW_NS:
            if candidate is None:
                candidate = track
            elif track.last_near_timestamp_ns > candidate.last_near_timestamp_ns:
                candidate = track

    if candidate is None:
        return None

    alert_timestamp_ns = volume_event.confirmation_timestamp_ns

    return AlertEvent(
        alert_id=(f"alert-{volume_event.event_id}-track-{candidate.track_id}"),
        shelf_id=volume_event.shelf_id,
        volume_event_id=volume_event.event_id,
        person_track_id=candidate.track_id,
        rule_version=RULE_VERSION,
        first_seen_timestamp_ns=volume_event.first_seen_timestamp_ns,
        alert_timestamp_ns=alert_timestamp_ns,
        missing_volume_m3=volume_event.missing_volume_m3,
        confidence=volume_event.confidence,
        reason="persistent removal near a non-authorized person track",
        evidence_frame_ids=volume_event.evidence_frame_ids,
    )

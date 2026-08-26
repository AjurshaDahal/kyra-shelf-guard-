from __future__ import annotations

import pytest

from kyra.contracts import ChangeType, VolumeChangeEvent


def make_volume_change_event() -> VolumeChangeEvent:
    return VolumeChangeEvent(
        event_id="volume-event-0001",
        shelf_id="shelf-01",
        change_type=ChangeType.REMOVAL,
        first_seen_timestamp_ns=2_000_000_000,
        confirmation_timestamp_ns=4_000_000_000,
        missing_volume_m3=0.0025,
        bounds_min_m=(-0.1, -0.2, 0.7),
        bounds_max_m=(0.1, 0.2, 0.9),
        centroid_m=(0.0, 0.0, 0.8),
        visible_shelf_fraction=0.85,
        confidence=0.92,
        evidence_frame_ids=("frame-0002", "frame-0003"),
    )


def test_volume_change_event_compatibility_fixture_preserves_contract_values() -> None:
    event = make_volume_change_event()

    assert event.event_id == "volume-event-0001"
    assert event.shelf_id == "shelf-01"
    assert event.change_type is ChangeType.REMOVAL
    assert event.first_seen_timestamp_ns == 2_000_000_000
    assert event.confirmation_timestamp_ns == 4_000_000_000
    assert event.missing_volume_m3 == pytest.approx(0.0025)
    assert event.bounds_min_m == (-0.1, -0.2, 0.7)
    assert event.bounds_max_m == (0.1, 0.2, 0.9)
    assert event.centroid_m == (0.0, 0.0, 0.8)
    assert event.visible_shelf_fraction == pytest.approx(0.85)
    assert event.confidence == pytest.approx(0.92)
    assert event.rejection_reason is None
    assert event.evidence_frame_ids == ("frame-0002", "frame-0003")


def test_volume_change_event_defaults_to_no_rejection_or_evidence() -> None:
    event = VolumeChangeEvent(
        event_id="volume-event-0002",
        shelf_id="shelf-01",
        change_type=ChangeType.UNKNOWN,
        first_seen_timestamp_ns=5_000_000_000,
        confirmation_timestamp_ns=5_000_000_001,
        missing_volume_m3=0.0,
        bounds_min_m=(0.0, 0.0, 0.0),
        bounds_max_m=(0.0, 0.0, 0.0),
        centroid_m=(0.0, 0.0, 0.0),
        visible_shelf_fraction=0.0,
        confidence=0.0,
    )

    assert event.rejection_reason is None
    assert event.evidence_frame_ids == ()

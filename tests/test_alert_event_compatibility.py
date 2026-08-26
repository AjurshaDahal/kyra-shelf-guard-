from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from kyra.contracts import AlertEvent


def make_alert_event() -> AlertEvent:
    return AlertEvent(
        alert_id="alert-0001",
        shelf_id="shelf-01",
        volume_event_id="volume-event-0001",
        person_track_id=17,
        rule_version="rule-1.0",
        first_seen_timestamp_ns=2_000_000_000,
        alert_timestamp_ns=4_000_000_000,
        missing_volume_m3=0.0025,
        confidence=0.93,
        reason="persistent removal near a non-authorized person track",
        evidence_frame_ids=("frame-0002", "frame-0003"),
    )


def test_alert_event_compatibility_fixture_preserves_contract_values() -> None:
    alert = make_alert_event()

    assert alert.alert_id == "alert-0001"
    assert alert.shelf_id == "shelf-01"
    assert alert.volume_event_id == "volume-event-0001"
    assert alert.person_track_id == 17
    assert alert.rule_version == "rule-1.0"
    assert alert.first_seen_timestamp_ns == 2_000_000_000
    assert alert.alert_timestamp_ns == 4_000_000_000
    assert alert.missing_volume_m3 == pytest.approx(0.0025)
    assert alert.confidence == pytest.approx(0.93)
    assert alert.reason == "persistent removal near a non-authorized person track"
    assert alert.evidence_frame_ids == ("frame-0002", "frame-0003")


def test_alert_event_is_frozen_and_defaults_to_no_evidence_frames() -> None:
    alert = AlertEvent(
        alert_id="alert-0002",
        shelf_id="shelf-01",
        volume_event_id="volume-event-0002",
        person_track_id=18,
        rule_version="rule-1.0",
        first_seen_timestamp_ns=5_000_000_000,
        alert_timestamp_ns=6_000_000_000,
        missing_volume_m3=0.001,
        confidence=0.8,
        reason="review required",
    )

    assert alert.evidence_frame_ids == ()
    with pytest.raises(FrozenInstanceError):
        alert.alert_id = "changed"  # type: ignore[misc]

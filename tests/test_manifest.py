from __future__ import annotations

import hashlib
from collections.abc import Callable
from pathlib import Path

import pytest
from pydantic import ValidationError

from kyra.manifest import (
    FrameRecord,
    ScenarioManifest,
    load_manifest,
    manifest_checksum,
    write_manifest,
)


def test_manifest_round_trip_is_canonical_and_checksum_matches_file(
    tmp_path: Path,
    make_manifest: Callable[..., ScenarioManifest],
) -> None:
    manifest = make_manifest()
    path = tmp_path / "nested" / "scenario.json"

    checksum = write_manifest(manifest, path)

    assert load_manifest(path) == manifest
    assert path.read_bytes().endswith(b"\n")
    assert checksum == hashlib.sha256(path.read_bytes()).hexdigest()
    assert manifest_checksum(load_manifest(path)) == manifest_checksum(manifest)


def test_manifest_checksum_changes_with_content(
    make_manifest: Callable[..., ScenarioManifest],
) -> None:
    original = make_manifest()
    changed = original.model_copy(update={"random_seed": 43})

    assert manifest_checksum(original) != manifest_checksum(changed)


def test_manifest_rejects_unknown_fields(
    make_manifest: Callable[..., ScenarioManifest],
) -> None:
    payload = make_manifest().model_dump(mode="json")
    payload["unexpected"] = "not allowed"

    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        ScenarioManifest.model_validate(payload)


def test_manifest_rejects_duplicate_frame_ids(
    make_manifest: Callable[..., ScenarioManifest],
) -> None:
    frames = [
        FrameRecord(
            frame_id="same-id",
            timestamp_ns=1,
            rgb_path="rgb/1.png",
            depth_path="depth/1.png",
        ),
        FrameRecord(
            frame_id="same-id",
            timestamp_ns=2,
            rgb_path="rgb/2.png",
            depth_path="depth/2.png",
        ),
    ]

    with pytest.raises(ValidationError, match="frame IDs must be unique"):
        make_manifest(frames=frames, baseline_frame_ids=["same-id"])


def test_manifest_rejects_unordered_timestamps(
    make_manifest: Callable[..., ScenarioManifest],
) -> None:
    frames = [
        FrameRecord(
            frame_id="later", timestamp_ns=2, rgb_path="r1.png", depth_path="d1.png"
        ),
        FrameRecord(
            frame_id="earlier", timestamp_ns=1, rgb_path="r2.png", depth_path="d2.png"
        ),
    ]

    with pytest.raises(ValidationError, match="ordered by timestamp"):
        make_manifest(frames=frames, baseline_frame_ids=["later"])


def test_manifest_rejects_missing_baseline_frame(
    make_manifest: Callable[..., ScenarioManifest],
) -> None:
    with pytest.raises(ValidationError, match="baseline frames missing"):
        make_manifest(baseline_frame_ids=["not-present"])


def test_manifest_rejects_invalid_calibration_shape(
    make_manifest: Callable[..., ScenarioManifest],
) -> None:
    with pytest.raises(ValidationError, match="intrinsics"):
        make_manifest(intrinsics=((1.0, 0.0), (0.0, 1.0)))

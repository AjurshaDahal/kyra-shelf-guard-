from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pytest

from kyra.contracts import ChangeType, SourceType
from kyra.golden_pack import (
    GOLDEN_PACK_STATUS,
    GOLDEN_SCENARIOS,
    generate_golden_pack,
)
from kyra.io import ScenarioFrameSource
from kyra.manifest import ShapeFamily, load_manifest

GOLDEN_PACK_ROOT = Path(__file__).parents[1] / "scenario-fixtures" / "golden"

TEXT_ASSET_SUFFIXES = {".json", ".toml", ".sha256", ".md", ".txt"}


def _canonical_bytes(path: Path) -> bytes:
    """Return content with CRLF normalized to LF for text assets.

    The inventory records the generator's LF output, but a Windows checkout
    under ``core.autocrlf=true`` delivers CRLF bytes for text assets.  Hashing
    canonically keeps the audit identical on Windows and on the target T4.
    """
    data = path.read_bytes()
    if path.suffix in TEXT_ASSET_SUFFIXES:
        data = data.replace(b"\r\n", b"\n")
    return data


def _sha256_inventory(root: Path) -> dict[str, str]:
    return {
        path.relative_to(root).as_posix(): hashlib.sha256(_canonical_bytes(path)).hexdigest()
        for path in sorted(root.rglob("*"))
        if path.is_file() and path.name != "checksums.sha256"
    }


def _recorded_checksums(root: Path) -> dict[str, str]:
    records: dict[str, str] = {}
    for line in (root / "checksums.sha256").read_text(encoding="utf-8").splitlines():
        digest, relative_path = line.split("  ", maxsplit=1)
        records[relative_path] = digest
    return records


def test_candidate_pack_covers_the_reviewed_matrix_and_replays() -> None:
    index = json.loads((GOLDEN_PACK_ROOT / "golden-pack.json").read_text(encoding="utf-8"))
    definitions = {definition.scenario_id: definition for definition in GOLDEN_SCENARIOS}

    assert index["schema_version"] == "1.0"
    assert index["pack_status"] == GOLDEN_PACK_STATUS == "frozen"
    assert index["decision_status"] == "D-009-confirmed-2026-09-06"
    assert index["scenario_count"] == 10
    assert len(index["scenarios"]) == 10
    assert [entry["scenario_id"] for entry in index["scenarios"]] == list(definitions)
    assert {entry["behavior"] for entry in index["scenarios"]} == {
        "no_change",
        "thin_item_removal",
        "irregular_item_removal",
        "addition",
        "person_only_occlusion",
        "removal_then_occlusion",
        "authorized_restocking",
        "lighting_variation",
        "invalid_depth",
        "camera_drift",
    }
    assert {entry["shape_family"] for entry in index["scenarios"]} == {
        family.value for family in ShapeFamily
    }

    for entry in index["scenarios"]:
        definition = definitions[entry["scenario_id"]]
        manifest_path = GOLDEN_PACK_ROOT / entry["manifest_path"]
        manifest = load_manifest(manifest_path)
        source = ScenarioFrameSource(manifest_path)

        assert manifest.schema_version == "1.1"
        assert manifest.scenario_id == definition.scenario_id
        assert manifest.random_seed == definition.settings.random_seed
        assert manifest.source_type is SourceType.SYNTHETIC_RGBD
        assert manifest.evidence_source == "synthetic"
        assert manifest.split == "golden"
        assert entry["expected_alert"] is definition.expected_alert
        assert entry["random_seed"] == manifest.random_seed
        assert entry["category"] == manifest.category
        assert entry["shape_family"] == definition.settings.shape_family.value
        assert entry["object_volume_m3"] > 0
        assert "\\" not in entry["manifest_path"]
        assert len(list(source)) == len(manifest.frames)
        assert all(
            frame.timestamp_ns < later.timestamp_ns
            for frame, later in zip(manifest.frames, manifest.frames[1:], strict=False)
        )


def test_candidate_pack_encodes_each_behavior_without_claiming_downstream_results() -> None:
    index = json.loads((GOLDEN_PACK_ROOT / "golden-pack.json").read_text(encoding="utf-8"))
    entries = {entry["behavior"]: entry for entry in index["scenarios"]}

    for behavior, entry in entries.items():
        manifest_path = GOLDEN_PACK_ROOT / entry["manifest_path"]
        manifest = load_manifest(manifest_path)
        source = ScenarioFrameSource(manifest_path)
        baseline = source.baseline_frames()[0]
        event_packets = list(source.event_frames())
        first_event = event_packets[0]
        object_mask = source.object_mask(first_event.frame_id)

        if behavior == "no_change":
            assert not manifest.ground_truth_events
            assert np.array_equal(first_event.rgb, baseline.rgb)
            assert np.array_equal(first_event.depth_m, baseline.depth_m)
        elif behavior in {"thin_item_removal", "irregular_item_removal"}:
            event = manifest.ground_truth_events[0]
            assert event.change_type is ChangeType.REMOVAL
            assert event.should_alert
            assert np.all(first_event.depth_m[object_mask] > baseline.depth_m[object_mask])
        elif behavior == "addition":
            event = manifest.ground_truth_events[0]
            assert event.change_type is ChangeType.ADDITION
            assert not event.should_alert
            assert np.all(first_event.depth_m[object_mask] < baseline.depth_m[object_mask])
        elif behavior == "person_only_occlusion":
            assert not manifest.ground_truth_events
            assert source.occlusion_mask(first_event.frame_id).any()
            assert source.track_annotations(first_event.frame_id)
            assert np.array_equal(first_event.depth_m, baseline.depth_m)
        elif behavior == "removal_then_occlusion":
            assert len(event_packets) == 2
            assert not source.occlusion_mask(event_packets[0].frame_id).any()
            assert source.occlusion_mask(event_packets[1].frame_id).any()
            assert np.all(first_event.depth_m[object_mask] > baseline.depth_m[object_mask])
        elif behavior == "authorized_restocking":
            event = manifest.ground_truth_events[0]
            assert manifest.system_mode == "RESTOCK_MODE"
            assert event.change_type is ChangeType.ADDITION
            assert not event.should_alert
            assert source.track_annotations(first_event.frame_id)[0].authorized
        elif behavior == "lighting_variation":
            assert not manifest.ground_truth_events
            assert not np.array_equal(first_event.rgb, baseline.rgb)
            assert np.array_equal(first_event.depth_m, baseline.depth_m)
        elif behavior == "invalid_depth":
            assert not manifest.ground_truth_events
            assert np.all(first_event.depth_m[object_mask] == 0)
            assert not first_event.valid_depth_mask[object_mask].any()
        elif behavior == "camera_drift":
            assert not manifest.ground_truth_events
            assert not np.array_equal(first_event.rgb, baseline.rgb)
            assert not first_event.valid_depth_mask.all()
        else:  # pragma: no cover - the exact behavior set is asserted above.
            raise AssertionError(f"unhandled golden behavior: {behavior}")


def test_candidate_pack_checksums_match_and_regeneration_is_byte_identical(
    tmp_path: Path,
) -> None:
    assert _recorded_checksums(GOLDEN_PACK_ROOT) == _sha256_inventory(GOLDEN_PACK_ROOT)

    regenerated = generate_golden_pack(tmp_path / "golden")

    assert _canonical_bytes(regenerated / "checksums.sha256") == _canonical_bytes(
        GOLDEN_PACK_ROOT / "checksums.sha256"
    )
    assert _sha256_inventory(regenerated) == _sha256_inventory(GOLDEN_PACK_ROOT)

    with pytest.raises(FileExistsError, match="output folder is not empty"):
        generate_golden_pack(regenerated)

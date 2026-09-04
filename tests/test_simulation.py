from __future__ import annotations

import hashlib
from pathlib import Path

import numpy as np
import pytest

from kyra.contracts import ChangeType, SourceType
from kyra.io import ScenarioFrameSource
from kyra.manifest import ShapeFamily, load_manifest
from kyra.simulation import ScenarioSettings, generate_scenario


def _sha256_tree(root: Path) -> dict[str, str]:
    return {
        path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def test_generate_scenario_is_byte_identical_for_same_seed_and_settings(
    tmp_path: Path,
) -> None:
    settings = ScenarioSettings(
        scenario_id="deterministic-cylinder-removal",
        random_seed=1729,
        category="canned-drink",
        shape_family=ShapeFamily.CYLINDER,
        change_type=ChangeType.REMOVAL,
        should_alert=True,
    )

    first = generate_scenario(tmp_path / "first", settings)
    second = generate_scenario(tmp_path / "second", settings)

    assert first.read_bytes() == second.read_bytes()
    assert _sha256_tree(first.parent) == _sha256_tree(second.parent)
    manifest_text = first.read_text(encoding="utf-8")
    assert "\\\\" not in manifest_text
    assert str(tmp_path) not in manifest_text


@pytest.mark.parametrize("shape_family", list(ShapeFamily))
def test_generated_scenario_replays_and_records_required_object_metadata(
    tmp_path: Path,
    shape_family: ShapeFamily,
) -> None:
    settings = ScenarioSettings(
        scenario_id=f"generated-{shape_family.value}",
        random_seed=41,
        category=f"test-{shape_family.value}",
        shape_family=shape_family,
        change_type=ChangeType.REMOVAL,
        should_alert=True,
    )

    manifest_path = generate_scenario(tmp_path / shape_family.value, settings)
    manifest = load_manifest(manifest_path)
    source = ScenarioFrameSource(manifest_path)

    assert manifest.schema_version == "1.1"
    assert manifest.random_seed == 41
    assert manifest.source_type is SourceType.SYNTHETIC_RGBD
    assert manifest.evidence_source == "synthetic"
    assert len(manifest.baseline_frame_ids) == 30
    assert len(manifest.frames) == 32
    assert [frame.timestamp_ns for frame in manifest.frames] == sorted(
        frame.timestamp_ns for frame in manifest.frames
    )
    assert all("\\" not in frame.rgb_path for frame in manifest.frames)

    event = manifest.ground_truth_events[0]
    event_record = next(
        frame
        for frame in manifest.frames
        if frame.timestamp_ns == event.first_seen_timestamp_ns
    )
    assert event.change_type is ChangeType.REMOVAL
    assert event.shape_family is shape_family
    assert event.volume_m3 > 0
    assert event.should_alert
    assert event_record.object_mask_path is not None
    assert all(
        shelf_min <= event_min < event_max <= shelf_max
        for shelf_min, event_min, event_max, shelf_max in zip(
            manifest.shelf.bounds_min_m,
            event.bounds_min_m,
            event.bounds_max_m,
            manifest.shelf.bounds_max_m,
            strict=True,
        )
    )

    baseline_packet = source.baseline_frames()[0]
    event_packet = next(source.event_frames())
    event_mask = source.object_mask(event_record.frame_id)
    assert baseline_packet.rgb.dtype == np.uint8
    assert baseline_packet.depth_m.dtype == np.float32
    assert baseline_packet.valid_depth_mask.dtype == bool
    assert event_mask.dtype == bool
    assert event_mask.any()
    assert not source.occlusion_mask(event_record.frame_id).any()
    assert np.all(
        event_packet.depth_m[event_mask] > baseline_packet.depth_m[event_mask]
    )


def test_different_seed_changes_randomized_assets(tmp_path: Path) -> None:
    common = dict(
        scenario_id="seeded-handled-removal",
        category="handled-bag",
        shape_family=ShapeFamily.HANDLED_OR_HANGING,
        change_type=ChangeType.REMOVAL,
        should_alert=True,
    )

    first = generate_scenario(
        tmp_path / "seed-1",
        ScenarioSettings(random_seed=1, **common),
    )
    second = generate_scenario(
        tmp_path / "seed-2",
        ScenarioSettings(random_seed=2, **common),
    )

    first_hashes = _sha256_tree(first.parent)
    second_hashes = _sha256_tree(second.parent)
    assert first.read_bytes() != second.read_bytes()
    assert first_hashes["masks/frame-0030-object.png"] != second_hashes[
        "masks/frame-0030-object.png"
    ]


def test_addition_scenario_places_object_after_baseline(tmp_path: Path) -> None:
    manifest_path = generate_scenario(
        tmp_path / "addition",
        ScenarioSettings(
            scenario_id="generated-cylinder-addition",
            random_seed=29,
            category="bottle",
            shape_family=ShapeFamily.CYLINDER,
            change_type=ChangeType.ADDITION,
            should_alert=False,
        ),
    )
    source = ScenarioFrameSource(manifest_path)
    baseline_packet = source.baseline_frames()[0]
    event_packet = next(source.event_frames())
    event_mask = source.object_mask(event_packet.frame_id)

    assert load_manifest(manifest_path).ground_truth_events[0].change_type is ChangeType.ADDITION
    assert np.all(
        event_packet.depth_m[event_mask] < baseline_packet.depth_m[event_mask]
    )


def test_generator_rejects_nonempty_output_folder(tmp_path: Path) -> None:
    output = tmp_path / "existing"
    output.mkdir()
    (output / "keep.txt").write_text("do not overwrite", encoding="utf-8")
    settings = ScenarioSettings(
        scenario_id="safe-output",
        random_seed=7,
        category="tray",
        shape_family=ShapeFamily.THIN_BOX_OR_TRAY,
        change_type=ChangeType.REMOVAL,
        should_alert=True,
    )

    with pytest.raises(FileExistsError, match="not empty"):
        generate_scenario(output, settings)

    assert (output / "keep.txt").read_text(encoding="utf-8") == "do not overwrite"

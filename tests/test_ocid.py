from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np
import pytest

from kyra.contracts import ChangeType, SourceType
from kyra.io import ScenarioFrameSource
from kyra.manifest import (
    ShapeFamily,
    ShelfConfigRecord,
    load_manifest,
)
from kyra.ocid import (
    derive_events,
    object_mask,
    ocid_depth_to_mm,
    parse_sequence_metadata,
    sha256_of_file,
    shape_family_for,
    valid_mask,
    write_converted_sequence,
)

FIXTURE = Path(__file__).parent / "fixtures" / "ocid-mini" / "ocid" / "sequence-01"


def _fixture_metadata() -> object:
    return parse_sequence_metadata((FIXTURE / "metadata.toml").read_text(encoding="utf-8"))


def _fixture_frames() -> list[tuple[np.ndarray, np.ndarray, np.ndarray]]:
    frames = []
    for index in range(3):
        rgb_bgr = cv2.imread(
            str(FIXTURE / f"frame-{index:06d}.color.png"), cv2.IMREAD_COLOR
        )
        raw_depth = cv2.imread(
            str(FIXTURE / f"frame-{index:06d}.depth.png"), cv2.IMREAD_UNCHANGED
        )
        segmentation = cv2.imread(
            str(FIXTURE / f"frame-{index:06d}.mask.png"), cv2.IMREAD_GRAYSCALE
        )
        assert rgb_bgr is not None and raw_depth is not None and segmentation is not None
        frames.append((rgb_bgr, raw_depth, segmentation))
    return frames


def _shelf() -> ShelfConfigRecord:
    return ShelfConfigRecord(
        shelf_id="shelf-ocid-01",
        roi_xyxy=(0, 0, 16, 16),
        bounds_min_m=(-0.2, -0.2, 0.5),
        bounds_max_m=(0.2, 0.2, 1.2),
    )


def test_parse_sequence_metadata_accepts_fixture() -> None:
    metadata = _fixture_metadata()

    assert metadata.database_name == "ocid-mini"
    assert metadata.camera.width == 16
    assert metadata.camera.height == 16
    assert metadata.camera.fx == pytest.approx(20.0)
    assert metadata.camera.depth_scale == pytest.approx(0.0001)
    assert [frame.frame_id for frame in metadata.frames] == [
        "frame-000000",
        "frame-000001",
        "frame-000002",
    ]
    assert len(metadata.frames[1].objects) == 1
    assert metadata.frames[1].objects[0].category == "cup"


def test_parse_sequence_metadata_rejects_missing_camera_fields() -> None:
    text = (FIXTURE / "metadata.toml").read_text(encoding="utf-8")
    text = text.replace("cy = 7.5\n", "")

    with pytest.raises(ValueError, match="camera table is missing fields"):
        parse_sequence_metadata(text)


def test_parse_sequence_metadata_rejects_duplicate_frame_ids() -> None:
    text = (FIXTURE / "metadata.toml").read_text(encoding="utf-8")
    text = text.replace('id = "frame-000002"', 'id = "frame-000000"')

    with pytest.raises(ValueError, match="duplicate OCID frame id"):
        parse_sequence_metadata(text)


def test_ocid_depth_maps_to_millimetres_and_keeps_zero_unknown() -> None:
    raw = np.array([[10000, 9500, 0]], dtype=np.uint16)

    depth_mm = ocid_depth_to_mm(raw, 0.0001)

    assert depth_mm.tolist() == [[1000, 950, 0]]
    assert depth_mm.dtype == np.uint16


def test_ocid_depth_rejects_unrepresentable_values() -> None:
    with pytest.raises(ValueError, match="cannot be stored in uint16 mm"):
        ocid_depth_to_mm(np.array([[65535]], dtype=np.uint16), 1.0)


def test_valid_mask_marks_only_positive_depth() -> None:
    mask = valid_mask(np.array([[10000, 0, 9500]], dtype=np.uint16))

    assert mask.tolist() == [[255, 0, 255]]


def test_object_mask_extracts_one_instance() -> None:
    segmentation = np.array([[0, 1, 1], [2, 2, 0]], dtype=np.uint8)

    mask = object_mask(segmentation, 2)

    assert mask.tolist() == [[0, 0, 0], [255, 255, 0]]


def test_shape_family_mapping_covers_oci_categories_and_falls_back() -> None:
    assert shape_family_for("cup") is ShapeFamily.CYLINDER
    assert shape_family_for("shoe") is ShapeFamily.IRREGULAR
    assert shape_family_for("mystery-object") is ShapeFamily.IRREGULAR


def test_derive_events_reports_addition_and_removal() -> None:
    metadata = _fixture_metadata()

    events = derive_events(metadata.frames)

    assert events == [(1, ChangeType.ADDITION, metadata.frames[1].objects[0])]


def test_derive_events_reports_removal_when_object_disappears() -> None:
    metadata = _fixture_metadata()
    frames = list(metadata.frames)
    frames[2] = frames[2].__class__(frame_id="frame-000002", objects=())

    events = derive_events(frames)

    assert (2, ChangeType.REMOVAL, frames[1].objects[0]) in events


def test_converted_sequence_writes_and_replays(tmp_path: Path) -> None:
    metadata = _fixture_metadata()
    destination = tmp_path / "converted"
    manifest, checksum = write_converted_sequence(
        metadata,
        _fixture_frames(),
        destination,
        shelf=_shelf(),
        scenario_id="ocid-mini-0001",
        seed=23,
    )

    assert (destination / "scenario.json").exists()
    assert len(checksum) == 64
    assert manifest.schema_version == "1.1"
    assert manifest.source_type is SourceType.PUBLIC_RGBD
    assert manifest.evidence_source == "public_rgbd"
    assert (destination / manifest.frames[0].rgb_path).exists()
    assert (destination / manifest.frames[0].depth_path).exists()
    assert (destination / manifest.frames[0].valid_mask_path).exists()
    assert manifest.frames[0].object_mask_path is None
    assert manifest.frames[1].object_mask_path is not None
    assert [frame.timestamp_ns for frame in manifest.frames] == [
        1_000_000_000,
        2_000_000_000,
        3_000_000_000,
    ]
    assert [frame.frame_id for frame in manifest.frames] == [
        "frame-000000",
        "frame-000001",
        "frame-000002",
    ]
    assert manifest.baseline_frame_ids == ["frame-000000"]
    assert len(manifest.ground_truth_events) == 1
    event = manifest.ground_truth_events[0]
    assert event.change_type is ChangeType.ADDITION
    assert event.first_seen_timestamp_ns == 2_000_000_000
    assert event.shape_family is ShapeFamily.CYLINDER
    assert event.should_alert is False

    loaded_manifest = load_manifest(destination / "scenario.json")
    assert loaded_manifest == manifest

    source = ScenarioFrameSource(destination / "scenario.json")
    assert len(source) == 3
    packet = source.get("frame-000001")
    assert packet.depth_m.shape == (16, 16)
    assert packet.depth_m[8, 8] == pytest.approx(0.95)
    assert packet.depth_m[0, 0] == pytest.approx(1.0)
    assert packet.source_type is SourceType.PUBLIC_RGBD
    object_mask_image = source.object_mask("frame-000001")
    assert object_mask_image[8, 8]


def test_reversed_sequence_becomes_removal_with_new_timestamps(
    tmp_path: Path,
) -> None:
    metadata = _fixture_metadata()
    destination = tmp_path / "reversed"
    manifest, _ = write_converted_sequence(
        metadata,
        _fixture_frames(),
        destination,
        shelf=_shelf(),
        scenario_id="ocid-mini-0001-reversed",
        seed=24,
        reverse=True,
        first_timestamp_ns=5_000_000_000,
    )

    assert [frame.frame_id for frame in manifest.frames] == [
        "frame-000002",
        "frame-000001",
        "frame-000000",
    ]
    assert [frame.timestamp_ns for frame in manifest.frames] == [
        5_000_000_000,
        6_000_000_000,
        7_000_000_000,
    ]
    assert manifest.baseline_frame_ids == ["frame-000002"]
    assert len(manifest.ground_truth_events) == 1
    event = manifest.ground_truth_events[0]
    assert event.change_type is ChangeType.REMOVAL
    assert event.first_seen_timestamp_ns == 7_000_000_000
    assert event.should_alert is True
    assert any("reversed" in note for note in manifest.notes)
    assert manifest.frames[2].object_mask_path is not None
    assert any("last-seen object region" in note for note in manifest.notes)

    source = ScenarioFrameSource(destination / "scenario.json")
    assert source.get("frame-000002").depth_m[8, 8] == pytest.approx(0.95)
    assert source.object_mask("frame-000002").shape == (16, 16)
    assert source.object_mask("frame-000002")[8, 8]


def test_source_checksum_gate_detects_tampering(tmp_path: Path) -> None:
    path = tmp_path / "metadata.toml"
    path.write_text(
        (FIXTURE / "metadata.toml").read_text(encoding="utf-8"), encoding="utf-8"
    )
    original = sha256_of_file(path)

    path.write_text(
        (FIXTURE / "metadata.toml").read_text(encoding="utf-8").replace(
            "ocid-mini", "ocid-tampered"
        ),
        encoding="utf-8",
    )

    assert sha256_of_file(path) != original
    assert len(original) == 64
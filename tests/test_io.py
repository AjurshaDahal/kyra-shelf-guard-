from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

import cv2
import numpy as np
import pytest

from kyra.contracts import SourceType
from kyra.io import ScenarioFrameSource
from kyra.manifest import ScenarioManifest, load_manifest, write_manifest


def _rewrite_manifest(
    path: Path,
    change: Callable[[dict[str, object]], None],
) -> None:
    payload = load_manifest(path).model_dump(mode="json")
    change(payload)
    write_manifest(ScenarioManifest.model_validate(payload), path)


def _write_png(path: Path, image: np.ndarray) -> None:
    if not cv2.imwrite(str(path), image):
        raise RuntimeError(f"OpenCV could not write test image {path}")


def test_scenario_source_replays_rgb_depth_masks_and_frame_groups(
    scenario_path: Path,
) -> None:
    source = ScenarioFrameSource(scenario_path)

    first_pass = list(source)
    second_pass = list(source)
    first = first_pass[0]

    assert len(source) == 2
    assert [packet.frame_id for packet in first_pass] == [
        "frame-0001",
        "frame-0002",
    ]
    assert [packet.frame_id for packet in second_pass] == [
        "frame-0001",
        "frame-0002",
    ]
    assert first.rgb.dtype == np.uint8
    np.testing.assert_array_equal(first.rgb[0, 0], np.array([20, 10, 5], dtype=np.uint8))
    assert first.depth_m.dtype == np.float32
    assert first.depth_m[0, 0] == pytest.approx(1.0)
    assert not first.valid_depth_mask[0, 1]
    assert not first.valid_depth_mask[0, 2]
    assert first.source_type is SourceType.SYNTHETIC_RGBD
    assert [packet.frame_id for packet in source.baseline_frames()] == ["frame-0001"]
    assert [packet.frame_id for packet in source.event_frames()] == ["frame-0002"]
    assert source.get("frame-0002").depth_m[0, 0] == pytest.approx(1.1)
    assert source.occlusion_mask("frame-0001")[1, 1]
    annotations = source.track_annotations("frame-0002")
    assert len(annotations) == 1
    assert annotations[0].track_id == 7
    assert annotations[0].near_shelf


def test_track_annotations_do_not_expose_mutable_manifest_state(
    scenario_path: Path,
) -> None:
    source = ScenarioFrameSource(scenario_path)

    returned = source.track_annotations("frame-0002")
    returned[0].authorized = True

    assert not source.track_annotations("frame-0002")[0].authorized


def test_source_rejects_missing_assets(scenario_path: Path) -> None:
    def change(payload: dict[str, object]) -> None:
        payload["frames"][0]["rgb_path"] = "rgb/missing.png"  # type: ignore[index]

    _rewrite_manifest(scenario_path, change)

    with pytest.raises(FileNotFoundError, match="could not read scenario asset"):
        ScenarioFrameSource(scenario_path).get("frame-0001")


def test_source_rejects_non_uint16_depth(scenario_path: Path) -> None:
    depth_path = scenario_path.parent / "depth" / "frame-0001.png"
    _write_png(depth_path, np.full((4, 5), 10, dtype=np.uint8))

    with pytest.raises(ValueError, match="single-channel uint16 PNG"):
        ScenarioFrameSource(scenario_path).get("frame-0001")


def test_source_rejects_rgb_depth_size_mismatch(scenario_path: Path) -> None:
    depth_path = scenario_path.parent / "depth" / "frame-0001.png"
    _write_png(depth_path, np.full((3, 5), 1000, dtype=np.uint16))

    with pytest.raises(ValueError, match="RGB and depth dimensions differ"):
        ScenarioFrameSource(scenario_path).get("frame-0001")


def test_source_rejects_valid_mask_size_mismatch(scenario_path: Path) -> None:
    mask_path = scenario_path.parent / "masks" / "frame-0001-valid.png"
    _write_png(mask_path, np.full((3, 5), 255, dtype=np.uint8))

    with pytest.raises(ValueError, match="valid-depth mask and depth dimensions differ"):
        ScenarioFrameSource(scenario_path).get("frame-0001")


def test_source_rejects_occlusion_mask_size_mismatch(scenario_path: Path) -> None:
    mask_path = scenario_path.parent / "masks" / "frame-0001-occlusion.png"
    _write_png(mask_path, np.full((3, 5), 255, dtype=np.uint8))

    with pytest.raises(ValueError, match="occlusion mask and depth dimensions differ"):
        ScenarioFrameSource(scenario_path).occlusion_mask("frame-0001")


def test_source_rejects_paths_outside_scenario_folder(
    scenario_path: Path,
    tmp_path: Path,
) -> None:
    outside = tmp_path / "outside.png"
    _write_png(outside, np.zeros((4, 5, 3), dtype=np.uint8))

    def change(payload: dict[str, object]) -> None:
        payload["frames"][0]["rgb_path"] = "../outside.png"  # type: ignore[index]

    _rewrite_manifest(scenario_path, change)

    with pytest.raises(ValueError, match="escapes scenario folder"):
        ScenarioFrameSource(scenario_path).get("frame-0001")


def test_source_reports_unknown_frame_id(scenario_path: Path) -> None:
    source = ScenarioFrameSource(scenario_path)

    with pytest.raises(KeyError, match="unknown frame ID"):
        source.get("not-present")
    with pytest.raises(KeyError, match="unknown frame ID"):
        source.track_annotations("not-present")

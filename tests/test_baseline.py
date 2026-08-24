from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path

import numpy as np
import pytest

from kyra.baseline import BaselineBuilder, MidasAnchorAligner, load_baseline, save_baseline
from kyra.contracts import BaselineArtifact, FramePacket, ShelfConfig


def _calibration_packets(
    make_frame_packet: Callable[..., FramePacket],
    count: int,
) -> list[FramePacket]:
    depth = np.ones((32, 32), dtype=np.float32)
    depth[10:22, 10:22] = 0.8
    return [
        make_frame_packet(
            frame_id=f"calibration-{index:04d}",
            timestamp_ns=index * 1_000_000_000,
            depth_m=depth.copy(),
        )
        for index in range(count)
    ]


@pytest.fixture
def baseline_artifact(
    make_frame_packet: Callable[..., FramePacket],
    shelf_config: ShelfConfig,
) -> BaselineArtifact:
    return BaselineBuilder().fit(
        _calibration_packets(make_frame_packet, 30),
        shelf_config,
    )


def test_baseline_requires_30_frames_and_builds_expected_structure(
    make_frame_packet: Callable[..., FramePacket],
    shelf_config: ShelfConfig,
) -> None:
    builder = BaselineBuilder()
    packets = _calibration_packets(make_frame_packet, 30)

    with pytest.raises(ValueError, match="at least 30 frames; got 29"):
        builder.fit(packets[:29], shelf_config)

    artifact = builder.fit(packets, shelf_config)

    assert artifact.metadata["calibration_frame_count"] == 30
    assert artifact.baseline_depth_m[0, 0] == pytest.approx(1.0)
    assert artifact.baseline_depth_m[15, 15] == pytest.approx(0.8)
    assert artifact.noise_sigma_m[0, 0] == pytest.approx(0.001)
    assert artifact.fixed_geometry_mask[0, 0]
    assert not artifact.fixed_geometry_mask[15, 15]
    assert len(artifact.portable_components) == 1
    assert 0 < artifact.portable_components[0].volume_m3 < 0.5
    assert artifact.occupancy_grid.ndim == 3
    assert np.count_nonzero(artifact.occupancy_grid) > 0
    assert len(artifact.calibration_checksum) == 64


def test_baseline_round_trip_preserves_arrays_and_does_not_recompute(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    baseline_artifact: BaselineArtifact,
) -> None:
    path = tmp_path / "baseline"
    npz_path, json_path = save_baseline(baseline_artifact, path)

    def fail_if_called(*args: object, **kwargs: object) -> None:
        raise AssertionError("baseline calibration was recomputed during load")

    monkeypatch.setattr(BaselineBuilder, "fit", fail_if_called)
    loaded = load_baseline(path)

    assert npz_path.exists()
    assert json_path.exists()
    assert loaded.schema_version == baseline_artifact.schema_version
    assert loaded.calibration_checksum == baseline_artifact.calibration_checksum
    assert loaded.portable_components == baseline_artifact.portable_components
    assert loaded.metadata == baseline_artifact.metadata
    np.testing.assert_array_equal(loaded.baseline_depth_m, baseline_artifact.baseline_depth_m)
    np.testing.assert_array_equal(loaded.valid_mask, baseline_artifact.valid_mask)
    np.testing.assert_array_equal(
        loaded.fixed_geometry_mask,
        baseline_artifact.fixed_geometry_mask,
    )
    np.testing.assert_array_equal(loaded.occupancy_grid, baseline_artifact.occupancy_grid)
    np.testing.assert_array_equal(loaded.noise_sigma_m, baseline_artifact.noise_sigma_m)


def test_baseline_loader_rejects_unknown_schema(
    tmp_path: Path,
    baseline_artifact: BaselineArtifact,
) -> None:
    npz_path, json_path = save_baseline(baseline_artifact, tmp_path / "baseline.npz")
    metadata = json.loads(json_path.read_text(encoding="utf-8"))
    metadata["schema_version"] = "999"
    json_path.write_text(json.dumps(metadata), encoding="utf-8")

    with pytest.raises(ValueError, match="unsupported baseline schema"):
        load_baseline(npz_path)


def test_midas_alignment_accepts_two_distinct_metric_anchors() -> None:
    relative = np.array([[1.0, 2.0], [np.nan, 0.0]], dtype=np.float32)
    anchors = [
        (np.array([[True, False], [False, False]]), 1.0),
        (np.array([[False, True], [False, False]]), 0.5),
    ]

    aligner = MidasAnchorAligner().fit(relative, anchors)
    aligned = aligner.align(relative)

    assert aligner.residual_m == pytest.approx(0.0)
    np.testing.assert_allclose(aligned, np.array([[1.0, 0.5], [0.0, 0.0]]))


def test_midas_alignment_rejects_missing_anchors() -> None:
    relative = np.array([[1.0, 2.0]])
    anchors = [(np.array([[True, False]]), 1.0)]

    with pytest.raises(ValueError, match="at least two"):
        MidasAnchorAligner().fit(relative, anchors)


def test_midas_alignment_rejects_repeated_predictions() -> None:
    relative = np.ones((1, 2), dtype=np.float32)
    anchors = [
        (np.array([[True, False]]), 1.0),
        (np.array([[False, True]]), 0.5),
    ]

    with pytest.raises(ValueError, match="two distinct relative depths"):
        MidasAnchorAligner().fit(relative, anchors)


def test_midas_alignment_rejects_inconsistent_anchors() -> None:
    relative = np.array([[1.0, 2.0, 3.0]], dtype=np.float32)
    anchors = [
        (np.array([[True, False, False]]), 1.0),
        (np.array([[False, True, False]]), 0.5),
        (np.array([[False, False, True]]), 1.0),
    ]

    with pytest.raises(ValueError, match="residual"):
        MidasAnchorAligner().fit(relative, anchors)


@pytest.mark.parametrize(
    ("anchors", "message"),
    [
        (
            [
                (np.array([[True, False]]), 0.0),
                (np.array([[False, True]]), 1.0),
            ],
            "anchor depths must be positive",
        ),
        (
            [
                (np.array([[False, False]]), 1.0),
                (np.array([[False, True]]), 0.5),
            ],
            "finite prediction",
        ),
    ],
)
def test_midas_alignment_rejects_invalid_anchor_values(
    anchors: list[tuple[np.ndarray, float]],
    message: str,
) -> None:
    with pytest.raises(ValueError, match=message):
        MidasAnchorAligner().fit(np.array([[1.0, 2.0]]), anchors)


def test_midas_alignment_rejects_align_before_fit() -> None:
    with pytest.raises(RuntimeError, match="has not been fitted"):
        MidasAnchorAligner().align(np.array([[1.0]], dtype=np.float32))

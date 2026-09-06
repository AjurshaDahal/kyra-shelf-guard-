from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path

import numpy as np
import pytest

from kyra.baseline import BaselineBuilder, MidasAnchorAligner, load_baseline, save_baseline
from kyra.contracts import BaselineArtifact, FramePacket, ShelfConfig, SourceType


def _calibration_packets(
    make_frame_packet: Callable[..., FramePacket],
    count: int,
    *,
    source_type: SourceType = SourceType.SYNTHETIC_RGBD,
) -> list[FramePacket]:
    depth = np.ones((32, 32), dtype=np.float32)
    depth[10:22, 10:22] = 0.8
    return [
        make_frame_packet(
            frame_id=f"calibration-{index:04d}",
            timestamp_ns=index * 1_000_000_000,
            depth_m=depth.copy(),
            source_type=source_type,
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
    assert artifact.portable_components[0].pixel_count == 144
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


def test_baseline_rejects_mixed_frame_resolutions(
    make_frame_packet: Callable[..., FramePacket],
    shelf_config: ShelfConfig,
) -> None:
    packets = _calibration_packets(make_frame_packet, 30)
    packets[5] = make_frame_packet(
        frame_id="wrong-resolution",
        timestamp_ns=5_000_000_000,
        depth_m=np.ones((16, 16), dtype=np.float32),
    )

    with pytest.raises(ValueError, match="same resolution"):
        BaselineBuilder().fit(packets, shelf_config)


def test_baseline_rejects_changed_intrinsics(
    make_frame_packet: Callable[..., FramePacket],
    shelf_config: ShelfConfig,
) -> None:
    packets = _calibration_packets(make_frame_packet, 30)
    packets[10].intrinsics[0, 0] = 101.0

    with pytest.raises(ValueError, match="intrinsics changed"):
        BaselineBuilder().fit(packets, shelf_config)


def test_baseline_rejects_unsafe_occupancy_grid_dimensions(
    make_frame_packet: Callable[..., FramePacket],
    shelf_config: ShelfConfig,
) -> None:
    unsafe = ShelfConfig(
        shelf_id=shelf_config.shelf_id,
        roi_xyxy=shelf_config.roi_xyxy,
        bounds_min_m=(-50.0, -50.0, 0.5),
        bounds_max_m=(50.0, 50.0, 2.0),
    )

    with pytest.raises(ValueError, match="unsafe occupancy-grid dimensions"):
        BaselineBuilder().fit(_calibration_packets(make_frame_packet, 30), unsafe)


def test_plain_empty_shelf_has_no_portable_components(
    make_frame_packet: Callable[..., FramePacket],
    shelf_config: ShelfConfig,
) -> None:
    depth = np.ones((32, 32), dtype=np.float32)
    packets = [
        make_frame_packet(
            frame_id=f"calibration-{index:04d}",
            timestamp_ns=index * 1_000_000_000,
            depth_m=depth.copy(),
        )
        for index in range(30)
    ]

    artifact = BaselineBuilder().fit(packets, shelf_config)

    assert artifact.portable_components == ()
    assert artifact.fixed_geometry_mask.all()


def test_baseline_noise_model_tracks_injected_jitter(
    make_frame_packet: Callable[..., FramePacket],
    shelf_config: ShelfConfig,
) -> None:
    rng = np.random.default_rng(7)
    noisy_patch = (slice(4, 10), slice(4, 10))
    depth = np.ones((32, 32), dtype=np.float32)
    packets = []
    for index in range(30):
        frame = depth.copy()
        frame[noisy_patch] += rng.uniform(0.0, 0.02, size=(6, 6)).astype(np.float32)
        packets.append(
            make_frame_packet(
                frame_id=f"calibration-{index:04d}",
                timestamp_ns=index * 1_000_000_000,
                depth_m=frame,
            )
        )

    artifact = BaselineBuilder().fit(packets, shelf_config)

    assert artifact.noise_sigma_m[noisy_patch].max() > 0.002
    assert artifact.noise_sigma_m[0, 0] == pytest.approx(0.001)
    assert artifact.valid_mask[noisy_patch].all()
    assert artifact.baseline_depth_m[noisy_patch].min() > 1.0 - 0.001
    assert artifact.baseline_depth_m[noisy_patch].max() < 1.0 + 0.021


def test_baseline_checksum_changes_with_shelf_configuration(
    make_frame_packet: Callable[..., FramePacket],
    shelf_config: ShelfConfig,
) -> None:
    packets = _calibration_packets(make_frame_packet, 30)
    first = BaselineBuilder().fit(packets, shelf_config)
    renamed = ShelfConfig(
        shelf_id="shelf-02",
        roi_xyxy=shelf_config.roi_xyxy,
        bounds_min_m=shelf_config.bounds_min_m,
        bounds_max_m=shelf_config.bounds_max_m,
    )

    second = BaselineBuilder().fit(packets, renamed)

    assert second.calibration_checksum != first.calibration_checksum


def test_baseline_checksum_changes_with_depth_content(
    make_frame_packet: Callable[..., FramePacket],
    shelf_config: ShelfConfig,
) -> None:
    packets = _calibration_packets(make_frame_packet, 30)
    first = BaselineBuilder().fit(packets, shelf_config)
    for packet in packets:
        packet.depth_m[7, 7] = 0.9

    second = BaselineBuilder().fit(packets, shelf_config)

    assert second.calibration_checksum != first.calibration_checksum


def test_baseline_checksum_absorbs_single_frame_outlier_pixel(
    make_frame_packet: Callable[..., FramePacket],
    shelf_config: ShelfConfig,
) -> None:
    packets = _calibration_packets(make_frame_packet, 30)
    first = BaselineBuilder().fit(packets, shelf_config)
    packets[0].depth_m[7, 7] = 0.9

    second = BaselineBuilder().fit(packets, shelf_config)

    assert second.calibration_checksum == first.calibration_checksum


def test_baseline_checksum_is_identical_across_repetitions(
    make_frame_packet: Callable[..., FramePacket],
    shelf_config: ShelfConfig,
) -> None:
    first = BaselineBuilder().fit(_calibration_packets(make_frame_packet, 30), shelf_config)
    second = BaselineBuilder().fit(_calibration_packets(make_frame_packet, 30), shelf_config)

    assert first.calibration_checksum == second.calibration_checksum


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


def test_midas_aligned_frames_label_the_artifact_approximate(
    make_frame_packet: Callable[..., FramePacket],
    shelf_config: ShelfConfig,
) -> None:
    aligned = BaselineBuilder().fit(
        _calibration_packets(make_frame_packet, 30, source_type=SourceType.MIDAS_ALIGNED),
        shelf_config,
    )
    synthetic = BaselineBuilder().fit(
        _calibration_packets(make_frame_packet, 30, source_type=SourceType.SYNTHETIC_RGBD),
        shelf_config,
    )

    assert aligned.approximate_metric is True
    assert synthetic.approximate_metric is False


def test_baseline_round_trip_preserves_approximate_metric_flag(
    tmp_path: Path,
    make_frame_packet: Callable[..., FramePacket],
    shelf_config: ShelfConfig,
) -> None:
    aligned = BaselineBuilder().fit(
        _calibration_packets(make_frame_packet, 30, source_type=SourceType.MIDAS_ALIGNED),
        shelf_config,
    )

    _, json_path = save_baseline(aligned, tmp_path / "baseline")
    loaded = load_baseline(tmp_path / "baseline")

    assert loaded.approximate_metric is True
    assert json.loads(json_path.read_text(encoding="utf-8"))["approximate_metric"] is True


def test_midas_align_leaves_negative_and_non_finite_inputs_unknown() -> None:
    relative = np.array([[1.0, 2.0, -1.0, np.nan]], dtype=np.float32)
    aligner = MidasAnchorAligner().fit(
        relative,
        [
            (np.array([[True, False, False, False]]), 1.0),
            (np.array([[False, True, False, False]]), 0.5),
        ],
    )

    aligned = aligner.align(relative)

    assert np.all(np.isfinite(aligned))
    assert aligned[0, 0] == pytest.approx(1.0)
    assert aligned[0, 1] == pytest.approx(0.5)
    assert aligned[0, 2] == 0.0
    assert aligned[0, 3] == 0.0


def test_midas_residual_limit_is_explicit_and_enforceable() -> None:
    relative = np.array([[1.0, 2.0, 2.01]], dtype=np.float32)
    anchors = [
        (np.array([[True, False, False]]), 1.0),
        (np.array([[False, True, False]]), 0.5),
        (np.array([[False, False, True]]), 0.5),
    ]

    with pytest.raises(ValueError, match="residual"):
        MidasAnchorAligner().fit(relative, anchors, maximum_residual_m=0.001)

    relaxed = MidasAnchorAligner().fit(relative, anchors, maximum_residual_m=0.5)

    assert relaxed.residual_m is not None
    assert 0 < relaxed.residual_m <= 0.5

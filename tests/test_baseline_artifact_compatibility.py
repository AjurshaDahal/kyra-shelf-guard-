from __future__ import annotations

from pathlib import Path

import numpy as np

from kyra.baseline import load_baseline, save_baseline
from kyra.contracts import BaselineArtifact, PortableComponent, SCHEMA_VERSION


def make_baseline_artifact() -> BaselineArtifact:
    return BaselineArtifact(
        shelf_id="compatibility-shelf-01",
        roi_xyxy=(1, 2, 3, 4),
        bounds_min_m=(-0.2, -0.3, 0.5),
        bounds_max_m=(0.2, 0.3, 1.2),
        baseline_depth_m=np.array([[1.0, 0.8], [0.0, 1.1]], dtype=np.float64),
        valid_mask=np.array([[1, 1], [0, 1]], dtype=np.uint8),
        fixed_geometry_mask=np.array([[True, False], [False, True]], dtype=bool),
        portable_components=(
            PortableComponent(
                component_id="portable-001",
                volume_m3=0.001,
                bounds_min_m=(-0.1, -0.1, 0.7),
                bounds_max_m=(0.1, 0.1, 0.9),
                pixel_count=2,
            ),
        ),
        occupancy_grid=np.array([[[0], [1]], [[1], [0]]], dtype=np.int16),
        noise_sigma_m=np.array([[0.001, 0.002], [0.0, 0.003]], dtype=np.float64),
        intrinsics=np.array(
            [[600.0, 0.0, 1.5], [0.0, 601.0, 1.0], [0.0, 0.0, 1.0]],
            dtype=np.float32,
        ),
        camera_to_shelf=np.array(
            [
                [1.0, 0.0, 0.0, 0.1],
                [0.0, 1.0, 0.0, 0.2],
                [0.0, 0.0, 1.0, 0.3],
                [0.0, 0.0, 0.0, 1.0],
            ],
            dtype=np.float32,
        ),
        calibration_checksum="a" * 64,
        approximate_metric=True,
        metadata={"source": "compatibility-fixture"},
    )


def test_baseline_artifact_compatibility_fixture_normalizes_runtime_arrays() -> None:
    artifact = make_baseline_artifact()

    assert artifact.schema_version == SCHEMA_VERSION
    assert artifact.baseline_depth_m.dtype == np.float32
    assert artifact.valid_mask.dtype == bool
    assert artifact.fixed_geometry_mask.dtype == bool
    assert artifact.noise_sigma_m.dtype == np.float32
    assert artifact.occupancy_grid.dtype == np.uint8
    assert artifact.intrinsics.dtype == np.float64
    assert artifact.camera_to_shelf.dtype == np.float64
    assert artifact.baseline_depth_m.shape == (2, 2)
    assert artifact.occupancy_grid.shape == (2, 2, 1)
    assert artifact.portable_components[0].volume_m3 == 0.001
    assert artifact.approximate_metric


def test_baseline_artifact_compatibility_fixture_round_trips_without_recalibration(
    tmp_path: Path,
) -> None:
    artifact = make_baseline_artifact()

    npz_path, json_path = save_baseline(artifact, tmp_path / "baseline")
    loaded = load_baseline(npz_path)

    assert json_path.exists()
    assert loaded.shelf_id == artifact.shelf_id
    assert loaded.roi_xyxy == artifact.roi_xyxy
    assert loaded.bounds_min_m == artifact.bounds_min_m
    assert loaded.bounds_max_m == artifact.bounds_max_m
    assert loaded.calibration_checksum == artifact.calibration_checksum
    assert loaded.schema_version == artifact.schema_version
    assert loaded.approximate_metric == artifact.approximate_metric
    assert loaded.portable_components == artifact.portable_components
    assert loaded.metadata == artifact.metadata
    np.testing.assert_array_equal(loaded.baseline_depth_m, artifact.baseline_depth_m)
    np.testing.assert_array_equal(loaded.valid_mask, artifact.valid_mask)
    np.testing.assert_array_equal(loaded.fixed_geometry_mask, artifact.fixed_geometry_mask)
    np.testing.assert_array_equal(loaded.occupancy_grid, artifact.occupancy_grid)
    np.testing.assert_array_equal(loaded.noise_sigma_m, artifact.noise_sigma_m)
    np.testing.assert_array_equal(loaded.intrinsics, artifact.intrinsics)
    np.testing.assert_array_equal(loaded.camera_to_shelf, artifact.camera_to_shelf)

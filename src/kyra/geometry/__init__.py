"""Person 2 geometry subpackage: registration, projection, clustering, and volume."""

from kyra.geometry.clustering import (
    Cluster3D,
    extract_3d_clusters,
)
from kyra.geometry.points import (
    project_camera_points_to_pixels,
    transform_points,
    unproject_depth_to_camera_points,
)
from kyra.geometry.provider import ShelfGeometryProvider
from kyra.geometry.registration import (
    RegistrationResult,
    estimate_rigid_transform,
    register_frame_to_baseline,
)
from kyra.geometry.temporal_state import (
    TemporalChangeTracker,
    update_baseline_after_restock,
)
from kyra.geometry.volume import (
    VolumeEstimate,
    estimate_cluster_volume,
)

__all__ = [
    "Cluster3D",
    "RegistrationResult",
    "ShelfGeometryProvider",
    "TemporalChangeTracker",
    "VolumeEstimate",
    "estimate_cluster_volume",
    "estimate_rigid_transform",
    "extract_3d_clusters",
    "project_camera_points_to_pixels",
    "register_frame_to_baseline",
    "transform_points",
    "unproject_depth_to_camera_points",
    "update_baseline_after_restock",
]

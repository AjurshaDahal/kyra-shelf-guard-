from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import platform
from collections import defaultdict
from pathlib import Path

import cv2
import numpy as np

from kyra.adapters import LazyUltralyticsTrackingProvider
from kyra.contracts import FramePacket, ShelfConfig, SourceType
from kyra.io import ScenarioFrameSource
from kyra.tracking.rgbd_localization import localize_tracks_from_rgbd


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def serialize_tracks(tracks) -> list[dict[str, object]]:
    return [
        {
            "track_id": track.track_id,
            "timestamp_ns": track.timestamp_ns,
            "box_xyxy": list(track.box_xyxy),
            "pose_keypoint_count": int(track.pose_keypoints_xyc.shape[0]),
            "position_m": track.position_m,
            "near_shelf": track.near_shelf,
        }
        for track in tracks
    ]


def positive_frames(image_path: Path) -> tuple[list[FramePacket], ShelfConfig]:
    image_bgr = cv2.imread(str(image_path), cv2.IMREAD_COLOR)
    if image_bgr is None:
        raise FileNotFoundError(f"could not read positive-control image: {image_path}")
    image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
    height, width = image_rgb.shape[:2]
    depth_m = np.ones((height, width), dtype=np.float32)
    valid_mask = np.ones((height, width), dtype=bool)
    intrinsics = np.array(
        [[width, 0.0, (width - 1) / 2], [0.0, width, (height - 1) / 2], [0.0, 0.0, 1.0]],
        dtype=np.float64,
    )
    frames = [
        FramePacket(
            frame_id=f"positive-{index}",
            timestamp_ns=index * 1_000_000_000,
            rgb=image_rgb.copy(),
            depth_m=depth_m.copy(),
            valid_depth_mask=valid_mask.copy(),
            intrinsics=intrinsics.copy(),
            camera_to_shelf=np.eye(4, dtype=np.float64),
            source_type=SourceType.PUBLIC_RGBD,
        )
        for index in (1, 2)
    ]
    shelf = ShelfConfig(
        shelf_id="positive-control",
        roi_xyxy=(0, 0, width, height),
        bounds_min_m=(-1.0, -1.0, 0.1),
        bounds_max_m=(1.0, 1.0, 5.0),
    )
    return frames, shelf


def common_track_ids(serialized: list[dict[str, object]]) -> list[int]:
    ids_by_time: dict[int, set[int]] = defaultdict(set)
    for track in serialized:
        ids_by_time[int(track["timestamp_ns"])].add(int(track["track_id"]))
    if len(ids_by_time) < 2:
        return []
    return sorted(set.intersection(*ids_by_time.values()))


def scenario_shelf(source: ScenarioFrameSource) -> ShelfConfig:
    shelf = source.manifest.shelf
    return ShelfConfig(
        shelf_id=shelf.shelf_id,
        roi_xyxy=shelf.roi_xyxy,
        bounds_min_m=shelf.bounds_min_m,
        bounds_max_m=shelf.bounds_max_m,
        voxel_size_m=shelf.voxel_size_m,
    )


def package_version(name: str) -> str:
    try:
        return importlib.metadata.version(name)
    except importlib.metadata.PackageNotFoundError:
        return "not-installed"


def run(args: argparse.Namespace) -> dict[str, object]:
    model_path = args.model.resolve()
    positive_image = args.positive_image.resolve()
    scenarios = [path.resolve() for path in args.scenario]
    for path in (model_path, positive_image, *scenarios):
        if not path.is_file():
            raise FileNotFoundError(path)

    positive_packet_list, positive_shelf = positive_frames(positive_image)
    positive_provider = LazyUltralyticsTrackingProvider(model=str(model_path))
    positive_tracks = serialize_tracks(
        localize_tracks_from_rgbd(
            positive_provider.track(positive_packet_list, positive_shelf),
            positive_packet_list,
            positive_shelf,
        )
    )
    continuity_ids = common_track_ids(positive_tracks)

    scenario_results: list[dict[str, object]] = []
    for scenario_path in scenarios:
        source = ScenarioFrameSource(scenario_path)
        frames = list(source)[:2]
        provider = LazyUltralyticsTrackingProvider(model=str(model_path))
        shelf = scenario_shelf(source)
        tracks = serialize_tracks(
            localize_tracks_from_rgbd(provider.track(frames, shelf), frames, shelf)
        )
        scenario_results.append(
            {
                "scenario_path": str(scenario_path),
                "scenario_sha256": sha256_file(scenario_path),
                "frame_ids": [frame.frame_id for frame in frames],
                "frame_count": len(frames),
                "track_count": len(tracks),
                "tracks": tracks,
                "interpretation": (
                    "observed detector output only; OCID has no person labels, so this is not "
                    "accuracy or false-positive evidence"
                ),
            }
        )

    import torch

    return {
        "schema_version": "1.0",
        "evidence_kind": "recorded-image pretrained detector/tracker smoke",
        "model": {
            "path": str(model_path),
            "bytes": model_path.stat().st_size,
            "sha256": sha256_file(model_path),
            "configuration": "YOLO11n detection, person class only, ByteTrack",
        },
        "positive_control": {
            "path": str(positive_image),
            "bytes": positive_image.stat().st_size,
            "sha256": sha256_file(positive_image),
            "frames": 2,
            "track_count": len(positive_tracks),
            "tracks": positive_tracks,
            "track_ids_present_in_both_frames": continuity_ids,
            "acceptance": bool(positive_tracks and continuity_ids),
        },
        "ocid": scenario_results,
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "torch": package_version("torch"),
            "ultralytics": package_version("ultralytics"),
            "cuda_available": torch.cuda.is_available(),
            "cuda_device": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
            "execution_device": "cuda" if torch.cuda.is_available() else "cpu",
        },
        "latency_measured": False,
        "claims": [
            "The pinned pretrained detector and ByteTrack executed through Kyra's adapter.",
            "The positive control produced a person track ID present in two frames.",
            "The positive-control tracks received metric positions and shelf-proximity state "
            "from the constructed depth frames.",
        ],
        "limitations": [
            "The detector model is pretrained rather than trained or validated by this project.",
            "The positive-control RGB is recorded, but its flat metric depth is constructed.",
            "Person position uses median depth from the inner detection box, not segmentation.",
            "OCID contains no person annotations and cannot establish tracking accuracy.",
            "Repeated positive-control frames are a continuity smoke check, not a video benchmark.",
            "No live camera, target-T4, latency, alert, recall, false-positive, "
            "or deployment claim.",
        ],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run Kyra's real YOLO11n + ByteTrack adapter on recorded images."
    )
    parser.add_argument("--model", required=True, type=Path)
    parser.add_argument("--positive-image", required=True, type=Path)
    parser.add_argument("--scenario", required=True, action="append", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = run(args)
    if not report["positive_control"]["acceptance"]:
        raise RuntimeError("positive control did not produce a persistent person track")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(args.output.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

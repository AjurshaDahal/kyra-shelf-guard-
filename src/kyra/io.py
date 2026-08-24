"""Replayable RGB-D scenario input.

The on-disk contract deliberately uses boring, lossless files: RGB and masks
are PNGs and depth is a 16-bit PNG whose values are millimetres.  This keeps a
scenario inspectable without the Kyra package and, unlike a video container,
does not silently change depth values.
"""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import cv2
import numpy as np

from kyra.contracts import FramePacket
from kyra.manifest import FrameRecord, ScenarioManifest, TrackAnnotation, load_manifest


def _read_required(path: Path, flags: int) -> np.ndarray:
    image = cv2.imread(str(path), flags)
    if image is None:
        raise FileNotFoundError(f"could not read scenario asset: {path}")
    return image


class ScenarioFrameSource:
    """Read :class:`FramePacket` objects from a scenario manifest.

    Relative paths are resolved relative to ``scenario.json``.  Iterating the
    source more than once is supported, which is useful when calibration and
    event replay use the same fixture.
    """

    def __init__(self, manifest_path: str | Path) -> None:
        self.manifest_path = Path(manifest_path).resolve()
        self.root = self.manifest_path.parent
        self.manifest: ScenarioManifest = load_manifest(self.manifest_path)
        self._records = {record.frame_id: record for record in self.manifest.frames}

    def __len__(self) -> int:
        return len(self.manifest.frames)

    def __iter__(self) -> Iterator[FramePacket]:
        for record in self.manifest.frames:
            yield self.read_record(record)

    def _asset_path(self, asset_path: str) -> Path:
        relative_path = Path(asset_path)
        if relative_path.is_absolute():
            raise ValueError(f"scenario asset path must be relative: {asset_path}")
        resolved_path = (self.root / relative_path).resolve()
        try:
            resolved_path.relative_to(self.root)
        except ValueError:
            raise ValueError(
                f"scenario asset path escapes scenario folder: {asset_path}"
            ) from None
        return resolved_path

    def read_record(self, record: FrameRecord) -> FramePacket:
        rgb_bgr = _read_required(self._asset_path(record.rgb_path), cv2.IMREAD_COLOR)
        rgb = cv2.cvtColor(rgb_bgr, cv2.COLOR_BGR2RGB)

        depth_mm = _read_required(
            self._asset_path(record.depth_path), cv2.IMREAD_UNCHANGED
        )
        if depth_mm.ndim != 2 or depth_mm.dtype != np.uint16:
            raise ValueError(
                f"depth must be a single-channel uint16 PNG in millimetres: "
                f"{record.depth_path} has shape={depth_mm.shape}, dtype={depth_mm.dtype}"
            )
        if rgb.shape[:2] != depth_mm.shape:
            raise ValueError(
                "RGB and depth dimensions differ: "
                f"{rgb.shape[:2]} != {depth_mm.shape}"
            )
        depth_m = depth_mm.astype(np.float32) * np.float32(0.001)

        if record.valid_mask_path:
            valid_image = _read_required(
                self._asset_path(record.valid_mask_path), cv2.IMREAD_GRAYSCALE
            )
            if valid_image.shape != depth_mm.shape:
                raise ValueError(
                    "valid-depth mask and depth dimensions differ: "
                    f"{valid_image.shape} != {depth_mm.shape}"
                )
            valid_mask = valid_image > 0
        else:
            valid_mask = depth_mm > 0
        valid_mask &= depth_mm > 0

        return FramePacket(
            frame_id=record.frame_id,
            timestamp_ns=record.timestamp_ns,
            rgb=rgb,
            depth_m=depth_m,
            valid_depth_mask=valid_mask,
            intrinsics=np.asarray(self.manifest.intrinsics, dtype=np.float64),
            camera_to_shelf=np.asarray(self.manifest.camera_to_shelf, dtype=np.float64),
            source_type=self.manifest.source_type,
        )

    def get(self, frame_id: str) -> FramePacket:
        try:
            record = self._records[frame_id]
        except KeyError as error:
            raise KeyError(f"unknown frame ID {frame_id!r}") from error
        return self.read_record(record)

    def baseline_frames(self) -> list[FramePacket]:
        return [self.get(frame_id) for frame_id in self.manifest.baseline_frame_ids]

    def event_frames(self) -> Iterator[FramePacket]:
        baseline_ids = set(self.manifest.baseline_frame_ids)
        for record in self.manifest.frames:
            if record.frame_id not in baseline_ids:
                yield self.read_record(record)

    def track_annotations(self, frame_id: str) -> tuple[TrackAnnotation, ...]:
        """Return copies of the saved track annotations for one frame."""
        try:
            record = self._records[frame_id]
        except KeyError as error:
            raise KeyError(f"unknown frame ID {frame_id!r}") from error
        return tuple(track.model_copy(deep=True) for track in record.tracks)

    def occlusion_mask(self, frame_id: str) -> np.ndarray:
        """Return a boolean person/occluder mask, or an all-clear mask."""
        try:
            record = self._records[frame_id]
        except KeyError as error:
            raise KeyError(f"unknown frame ID {frame_id!r}") from error
        if record.occlusion_mask_path is None:
            frame = self.get(frame_id)
            return np.zeros(frame.depth_m.shape, dtype=bool)
        mask = _read_required(
            self._asset_path(record.occlusion_mask_path), cv2.IMREAD_GRAYSCALE
        )
        depth_shape = self.get(frame_id).depth_m.shape
        if mask.shape != depth_shape:
            raise ValueError(
                "occlusion mask and depth dimensions differ: "
                f"{mask.shape} != {depth_shape}"
            )
        return mask > 0


# Public name used in the architecture document.
FrameSource = ScenarioFrameSource

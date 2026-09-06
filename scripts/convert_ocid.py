"""Convert an OCID archive sequence into a Kyra manifest 1.1 scenario.

Filesystem discovery and the checksum gate live here; all mapping semantics
live in :mod:`kyra.ocid`.

Note: this script is intentionally not pushed to the repository while issue
#18 is open, because the change-impact classifier treats every ``scripts/*.py``
change as Person 4/governance.  It is reviewed and pushed together with the
narrow classifier fix.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import cv2

from kyra.manifest import ShelfConfigRecord
from kyra.ocid import (
    parse_sequence_metadata,
    sha256_of_file,
    write_converted_sequence,
)


def discover_frames(sequence_dir: Path) -> list[Path]:
    candidates = sorted(sequence_dir.glob("frame-*.color.png"))
    if not candidates:
        raise ValueError(f"no OCID frames found under {sequence_dir}")
    return candidates


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="OCID sequence folder with metadata.toml")
    parser.add_argument("output", type=Path, help="destination scenario folder")
    parser.add_argument("--shelf", type=Path, required=True, help="ShelfConfigRecord JSON")
    parser.add_argument("--expected-sha256", required=True, help="source archive checksum")
    parser.add_argument("--reverse", action="store_true", help="play the sequence backwards")
    parser.add_argument("--seed", type=int, default=1, help="determinism seed for metadata")
    parser.add_argument("--scenario-id", required=True, help="scenario identifier")
    parser.add_argument("--first-timestamp-ns", type=int, default=1_000_000_000)
    parser.add_argument("--frame-step-ns", type=int, default=1_000_000_000)
    args = parser.parse_args(argv)

    metadata_path = args.source / "metadata.toml"
    if not metadata_path.exists():
        print(f"error: missing {metadata_path}", file=sys.stderr)
        return 2
    actual = sha256_of_file(metadata_path)
    if actual.lower() != args.expected_sha256.lower():
        print(
            f"error: source checksum mismatch: expected {args.expected_sha256}, got {actual}",
            file=sys.stderr,
        )
        return 2

    shelf_payload = json.loads(args.shelf.read_text(encoding="utf-8"))
    shelf = ShelfConfigRecord.model_validate(shelf_payload)

    color_paths = discover_frames(args.source)
    frames = []
    for color_path in color_paths:
        depth_path = color_path.with_name(color_path.name.replace(".color.png", ".depth.png"))
        mask_path = color_path.with_name(color_path.name.replace(".color.png", ".mask.png"))
        rgb_bgr = cv2.imread(str(color_path), cv2.IMREAD_COLOR)
        raw_depth = cv2.imread(str(depth_path), cv2.IMREAD_UNCHANGED)
        segmentation = cv2.imread(str(mask_path), cv2.IMREAD_GRAYSCALE)
        if rgb_bgr is None or raw_depth is None or segmentation is None:
            raise ValueError(f"failed to read frame assets for {color_path}")
        frames.append((rgb_bgr, raw_depth, segmentation))

    metadata = parse_sequence_metadata(metadata_path.read_text(encoding="utf-8"))
    manifest, checksum = write_converted_sequence(
        metadata,
        frames,
        args.output,
        shelf=shelf,
        scenario_id=args.scenario_id,
        seed=args.seed,
        reverse=args.reverse,
        first_timestamp_ns=args.first_timestamp_ns,
        frame_step_ns=args.frame_step_ns,
    )
    print(f"wrote scenario {manifest.scenario_id} with {len(manifest.frames)} frames")
    print(f"manifest sha256: {checksum}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
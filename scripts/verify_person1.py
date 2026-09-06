"""Single Person 1 acceptance verification entry point.

Runs schema, golden-checksum, reader, baseline, MiDaS-policy, and provenance
checks with clear per-check messages and exits 0 only when every check passes.
The script never downloads anything.  When the golden pack fixtures are absent
(for example because P1-04 has not merged yet) it fails with an explicit
message instead of silently skipping the pack checks.

Note: this script is intentionally not pushed while issue #18 is open, because
the change-impact classifier treats every ``scripts/*.py`` change as Person
4/governance.  It is reviewed and pushed together with the narrow classifier
fix.
"""

from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path

import numpy as np

from kyra.baseline import BaselineBuilder, MidasAnchorAligner
from kyra.contracts import ShelfConfig
from kyra.io import ScenarioFrameSource
from kyra.manifest import load_manifest

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_GOLDEN = REPO_ROOT / "scenario-fixtures" / "golden"
DEFAULT_PROVENANCE = REPO_ROOT / "data-sources" / "provenance.json"

TEXT_ASSET_SUFFIXES = {".json", ".toml", ".sha256", ".md", ".txt"}

PROVENANCE_REQUIRED_STRINGS = (
    "source_id",
    "name",
    "official_url",
    "terms_url",
    "selected_subset",
    "conversion_command",
    "output_schema_version",
    "local_path_hint",
    "attribution",
    "status",
    "licence_review_status",
)
PROVENANCE_REQUIRED_NULLABLE = (
    "source_version",
    "downloaded_filename",
    "downloaded_bytes",
    "published_checksum",
    "computed_sha256",
)
PROVENANCE_STATUSES = {"pending_download", "retrieved", "converted", "excluded"}


def _sha256_of_file(path: Path, *, canonicalize_newlines: bool = False) -> str:
    data = path.read_bytes()
    if canonicalize_newlines:
        data = data.replace(b"\r\n", b"\n")
    return hashlib.sha256(data).hexdigest()


def _asset_digest(path: Path) -> str:
    """Hash assets canonically so Windows CRLF and Unix LF trees agree.

    The pack inventory records byte-for-byte hashes of the generator's LF
    output.  Git checkouts under ``core.autocrlf=true`` (or transport
    archives) deliver CRLF bytes for text assets, so comparing raw bytes
    would make the same pack fail on Windows and pass on the target T4.
    Text assets are therefore normalized to LF before hashing; binary assets
    are hashed verbatim.
    """
    return _sha256_of_file(path, canonicalize_newlines=path.suffix in TEXT_ASSET_SUFFIXES)


def _scenario_dirs(golden: Path) -> list[Path]:
    return sorted(path for path in golden.iterdir() if path.is_dir())


def check_golden_pack_present(golden: Path) -> list[str]:
    if not golden.is_dir():
        return [
            f"golden pack not found at {golden}; "
            "it will exist on origin/main only after P1-04 (issue #17) merges"
        ]
    manifests = sorted(golden.glob("*/scenario.json"))
    if not manifests:
        return [f"golden pack at {golden} contains no scenario manifests"]
    return []


def _pack_gate(golden: Path) -> list[str]:
    if check_golden_pack_present(golden):
        return ["skipped: golden pack is absent (see the 'golden pack present' check)"]
    return []


def check_manifest_schema(golden: Path) -> list[str]:
    if _pack_gate(golden):
        return _pack_gate(golden)
    errors: list[str] = []
    for manifest_path in sorted(golden.glob("*/scenario.json")):
        try:
            load_manifest(manifest_path)
        except Exception as error:  # noqa: BLE001 - surface any schema failure
            errors.append(f"{manifest_path.parent.name}: manifest invalid: {error}")
    return errors


def check_golden_checksums(golden: Path) -> list[str]:
    if _pack_gate(golden):
        return _pack_gate(golden)
    errors: list[str] = []
    inventory = golden / "checksums.sha256"
    if not inventory.is_file():
        return [f"missing checksum inventory: {inventory}"]
    expected: dict[str, str] = {}
    for line in inventory.read_text(encoding="utf-8").splitlines():
        parts = line.split()
        if len(parts) != 2:
            errors.append(f"malformed inventory line: {line!r}")
            continue
        expected[parts[1]] = parts[0]
    listed = set(expected)
    present = {path.relative_to(golden).as_posix() for path in golden.rglob("*") if path.is_file()}
    present.discard("checksums.sha256")
    for relative in sorted(listed - present):
        errors.append(f"checksum inventory lists missing file: {relative}")
    for relative in sorted(present - listed):
        errors.append(f"committed file is not in checksum inventory: {relative}")
    for relative, wanted in sorted(expected.items()):
        path = golden / relative
        if not path.is_file():
            continue
        actual = _asset_digest(path)
        if actual != wanted:
            errors.append(f"checksum mismatch for {relative}: got {actual}, want {wanted}")
    return errors


def check_reader(golden: Path) -> list[str]:
    if _pack_gate(golden):
        return _pack_gate(golden)
    errors: list[str] = []
    for manifest_path in sorted(golden.glob("*/scenario.json")):
        scenario = manifest_path.parent.name
        try:
            source = ScenarioFrameSource(manifest_path)
        except Exception as error:  # noqa: BLE001
            errors.append(f"{scenario}: reader cannot open scenario: {error}")
            continue
        for record in source.manifest.frames:
            try:
                packet = source.get(record.frame_id)
                if record.occlusion_mask_path:
                    occlusion = source.occlusion_mask(record.frame_id)
                    if occlusion.shape != packet.depth_m.shape:
                        errors.append(
                            f"{scenario}/{record.frame_id}: occlusion mask "
                            f"{occlusion.shape} != depth {packet.depth_m.shape}"
                        )
                if record.object_mask_path:
                    object_mask = source.object_mask(record.frame_id)
                    if object_mask.shape != packet.depth_m.shape:
                        errors.append(
                            f"{scenario}/{record.frame_id}: object mask "
                            f"{object_mask.shape} != depth {packet.depth_m.shape}"
                        )
            except Exception as error:  # noqa: BLE001
                errors.append(f"{scenario}/{record.frame_id}: reader failed: {error}")
    return errors


def check_baseline(golden: Path) -> list[str]:
    if _pack_gate(golden):
        return _pack_gate(golden)
    errors: list[str] = []
    for manifest_path in sorted(golden.glob("*/scenario.json")):
        scenario = manifest_path.parent.name
        try:
            source = ScenarioFrameSource(manifest_path)
            baseline_frames = source.baseline_frames()
            if not baseline_frames:
                errors.append(f"{scenario}: manifest declares no baseline frames")
                continue
            shelf = ShelfConfig(**source.manifest.shelf.c007_values)
            artifact = BaselineBuilder(minimum_frames=len(baseline_frames)).fit(
                baseline_frames, shelf
            )
            if not artifact.calibration_checksum:
                errors.append(f"{scenario}: baseline artifact has no checksum")
        except Exception as error:  # noqa: BLE001
            errors.append(f"{scenario}: baseline fit failed: {error}")
    return errors


def check_midas_policy() -> list[str]:
    errors: list[str] = []
    relative = np.array([[1.0, 2.0], [np.nan, 0.0]], dtype=np.float32)
    anchors = [
        (np.array([[True, False], [False, False]]), 1.0),
        (np.array([[False, True], [False, False]]), 0.5),
    ]
    try:
        aligner = MidasAnchorAligner().fit(relative, anchors)
        aligned = aligner.align(relative)
    except Exception as error:  # noqa: BLE001
        return [f"MiDaS anchor alignment failed: {error}"]
    if not np.all(np.isfinite(aligned)):
        errors.append("MiDaS aligned output contains non-finite values")
    if not np.allclose(aligned, [[1.0, 0.5], [0.0, 0.0]]):
        errors.append("MiDaS aligned output does not match the expected anchors")
    return errors


def check_provenance(provenance_path: Path) -> list[str]:
    errors: list[str] = []
    if not provenance_path.is_file():
        return [f"provenance record not found: {provenance_path}"]
    try:
        import json

        payload = json.loads(provenance_path.read_text(encoding="utf-8"))
    except Exception as error:  # noqa: BLE001
        return [f"provenance record is not valid JSON: {error}"]
    sources = payload.get("sources")
    if not isinstance(sources, list) or not sources:
        return ["provenance record must list at least one source"]
    for index, record in enumerate(sources):
        label = f"sources[{index}]"
        for field in PROVENANCE_REQUIRED_STRINGS:
            if not str(record.get(field, "")).strip():
                errors.append(f"{label}: missing required field {field}")
        for field in PROVENANCE_REQUIRED_NULLABLE:
            if field not in record:
                errors.append(f"{label}: missing field {field}")
        if record.get("status") not in PROVENANCE_STATUSES:
            errors.append(f"{label}: unknown status {record.get('status')!r}")
        path_hint = str(record.get("local_path_hint", ""))
        if any(marker in path_hint for marker in ("\\Users\\", "/Users/", "C:\\", "C:/")):
            errors.append(f"{label}: local_path_hint must not expose a private home path")
        exclusions = record.get("exclusions")
        if not isinstance(exclusions, list) or not exclusions:
            errors.append(f"{label}: exclusions must be a non-empty list")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--golden",
        type=Path,
        default=DEFAULT_GOLDEN,
        help="golden pack folder (default: scenario-fixtures/golden)",
    )
    parser.add_argument(
        "--provenance",
        type=Path,
        default=DEFAULT_PROVENANCE,
        help="provenance record (default: data-sources/provenance.json)",
    )
    args = parser.parse_args(argv)

    checks = [
        ("golden pack present", check_golden_pack_present(args.golden)),
        ("manifest schema", check_manifest_schema(args.golden)),
        ("golden checksums", check_golden_checksums(args.golden)),
        ("reader replay", check_reader(args.golden)),
        ("baseline build", check_baseline(args.golden)),
        ("MiDaS policy", check_midas_policy()),
        ("provenance record", check_provenance(args.provenance)),
    ]
    failed = False
    for name, errors in checks:
        if errors:
            failed = True
            print(f"[FAIL] {name}")
            for error in errors:
                print(f"       - {error}")
        else:
            print(f"[OK]   {name}")
    if not failed:
        print("All Person 1 acceptance checks passed.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
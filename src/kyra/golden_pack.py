"""Composition and checksum inventory for the Person 1 golden scenario pack."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import numpy as np

from kyra.contracts import ChangeType
from kyra.io import ScenarioFrameSource
from kyra.manifest import ShapeFamily, load_manifest
from kyra.simulation import ScenarioCondition, ScenarioSettings, generate_scenario

GOLDEN_PACK_SCHEMA_VERSION = "1.0"
GOLDEN_PACK_STATUS = "candidate"
GOLDEN_PACK_DECISION_STATUS = "D-009-provisional-team-confirmation-required"


@dataclass(frozen=True, slots=True)
class GoldenScenarioDefinition:
    """One reviewed row in the candidate golden scenario matrix."""

    scenario_id: str
    directory_name: str
    behavior: str
    expected_result: str
    expected_alert: bool
    settings: ScenarioSettings


def _settings(
    *,
    scenario_id: str,
    random_seed: int,
    category: str,
    shape_family: ShapeFamily,
    change_type: ChangeType | None,
    should_alert: bool,
    condition: ScenarioCondition = ScenarioCondition.OBJECT_CHANGE,
    system_mode: Literal["NORMAL", "RESTOCK_MODE"] = "NORMAL",
) -> ScenarioSettings:
    return ScenarioSettings(
        scenario_id=scenario_id,
        random_seed=random_seed,
        category=category,
        shape_family=shape_family,
        change_type=change_type,
        should_alert=should_alert,
        condition=condition,
        system_mode=system_mode,
        split="golden",
        width=32,
        height=24,
        baseline_frame_count=1,
        event_frame_count=(
            2 if condition is ScenarioCondition.REMOVAL_THEN_OCCLUSION else 1
        ),
    )


GOLDEN_SCENARIOS = (
    GoldenScenarioDefinition(
        scenario_id="G01",
        directory_name="G01-no-change",
        behavior="no_change",
        expected_result="no_alert",
        expected_alert=False,
        settings=_settings(
            scenario_id="G01",
            random_seed=1101,
            category="stable-tray",
            shape_family=ShapeFamily.THIN_BOX_OR_TRAY,
            change_type=None,
            should_alert=False,
            condition=ScenarioCondition.NO_CHANGE,
        ),
    ),
    GoldenScenarioDefinition(
        scenario_id="G02",
        directory_name="G02-thin-item-removal",
        behavior="thin_item_removal",
        expected_result="alert",
        expected_alert=True,
        settings=_settings(
            scenario_id="G02",
            random_seed=1102,
            category="envelope",
            shape_family=ShapeFamily.THIN_BOX_OR_TRAY,
            change_type=ChangeType.REMOVAL,
            should_alert=True,
        ),
    ),
    GoldenScenarioDefinition(
        scenario_id="G03",
        directory_name="G03-irregular-item-removal",
        behavior="irregular_item_removal",
        expected_result="alert",
        expected_alert=True,
        settings=_settings(
            scenario_id="G03",
            random_seed=1103,
            category="shoe",
            shape_family=ShapeFamily.IRREGULAR,
            change_type=ChangeType.REMOVAL,
            should_alert=True,
        ),
    ),
    GoldenScenarioDefinition(
        scenario_id="G04",
        directory_name="G04-addition",
        behavior="addition",
        expected_result="no_removal_alert",
        expected_alert=False,
        settings=_settings(
            scenario_id="G04",
            random_seed=1104,
            category="bottle",
            shape_family=ShapeFamily.CYLINDER,
            change_type=ChangeType.ADDITION,
            should_alert=False,
        ),
    ),
    GoldenScenarioDefinition(
        scenario_id="G05",
        directory_name="G05-person-only-occlusion",
        behavior="person_only_occlusion",
        expected_result="no_alert",
        expected_alert=False,
        settings=_settings(
            scenario_id="G05",
            random_seed=1105,
            category="handled-bag",
            shape_family=ShapeFamily.HANDLED_OR_HANGING,
            change_type=None,
            should_alert=False,
            condition=ScenarioCondition.PERSON_ONLY_OCCLUSION,
        ),
    ),
    GoldenScenarioDefinition(
        scenario_id="G06",
        directory_name="G06-removal-then-occlusion",
        behavior="removal_then_occlusion",
        expected_result="alert_after_visible_evidence",
        expected_alert=True,
        settings=_settings(
            scenario_id="G06",
            random_seed=1106,
            category="handled-container",
            shape_family=ShapeFamily.HANDLED_OR_HANGING,
            change_type=ChangeType.REMOVAL,
            should_alert=True,
            condition=ScenarioCondition.REMOVAL_THEN_OCCLUSION,
        ),
    ),
    GoldenScenarioDefinition(
        scenario_id="G07",
        directory_name="G07-authorized-restocking",
        behavior="authorized_restocking",
        expected_result="no_suspicious_alert",
        expected_alert=False,
        settings=_settings(
            scenario_id="G07",
            random_seed=1107,
            category="restocked-can",
            shape_family=ShapeFamily.CYLINDER,
            change_type=ChangeType.ADDITION,
            should_alert=False,
            system_mode="RESTOCK_MODE",
        ),
    ),
    GoldenScenarioDefinition(
        scenario_id="G08",
        directory_name="G08-lighting-variation",
        behavior="lighting_variation",
        expected_result="no_alert",
        expected_alert=False,
        settings=_settings(
            scenario_id="G08",
            random_seed=1108,
            category="stable-shoe",
            shape_family=ShapeFamily.IRREGULAR,
            change_type=None,
            should_alert=False,
            condition=ScenarioCondition.LIGHTING_VARIATION,
        ),
    ),
    GoldenScenarioDefinition(
        scenario_id="G09",
        directory_name="G09-invalid-depth",
        behavior="invalid_depth",
        expected_result="no_alert_from_unknown_depth",
        expected_alert=False,
        settings=_settings(
            scenario_id="G09",
            random_seed=1109,
            category="hanging-item",
            shape_family=ShapeFamily.HANDLED_OR_HANGING,
            change_type=None,
            should_alert=False,
            condition=ScenarioCondition.INVALID_DEPTH,
        ),
    ),
    GoldenScenarioDefinition(
        scenario_id="G10",
        directory_name="G10-camera-drift",
        behavior="camera_drift",
        expected_result="reject_or_suppress",
        expected_alert=False,
        settings=_settings(
            scenario_id="G10",
            random_seed=1110,
            category="drifted-tray",
            shape_family=ShapeFamily.THIN_BOX_OR_TRAY,
            change_type=None,
            should_alert=False,
            condition=ScenarioCondition.CAMERA_DRIFT,
        ),
    ),
)


def _sha256_inventory(root: Path) -> dict[str, str]:
    return {
        path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(root.rglob("*"))
        if path.is_file() and path.name != "checksums.sha256"
    }


def _object_volume_m3(manifest_path: Path) -> float:
    manifest = load_manifest(manifest_path)
    if manifest.ground_truth_events:
        return manifest.ground_truth_events[0].volume_m3

    source = ScenarioFrameSource(manifest_path)
    packet = source.baseline_frames()[0]
    object_mask = source.object_mask(packet.frame_id)
    valid_object = object_mask & packet.valid_depth_mask
    valid_background = ~object_mask & packet.valid_depth_mask
    object_depth_m = float(np.median(packet.depth_m[valid_object]))
    background_depth_m = float(np.median(packet.depth_m[valid_background]))
    thickness_m = background_depth_m - object_depth_m
    shelf_width_m = manifest.shelf.bounds_max_m[0] - manifest.shelf.bounds_min_m[0]
    shelf_height_m = manifest.shelf.bounds_max_m[1] - manifest.shelf.bounds_min_m[1]
    pixel_area_m2 = shelf_width_m * shelf_height_m / object_mask.size
    return float(np.count_nonzero(object_mask)) * pixel_area_m2 * thickness_m


def generate_golden_pack(destination: str | Path) -> Path:
    """Write the deterministic candidate pack and return its root directory."""

    root = Path(destination)
    if root.exists():
        if not root.is_dir() or any(root.iterdir()):
            raise FileExistsError(f"golden-pack output folder is not empty: {root}")
    else:
        root.mkdir(parents=True)

    entries: list[dict[str, object]] = []
    for definition in GOLDEN_SCENARIOS:
        manifest_path = generate_scenario(root / definition.directory_name, definition.settings)
        manifest = load_manifest(manifest_path)
        event = manifest.ground_truth_events[0] if manifest.ground_truth_events else None
        entries.append(
            {
                "scenario_id": definition.scenario_id,
                "manifest_path": manifest_path.relative_to(root).as_posix(),
                "behavior": definition.behavior,
                "expected_result": definition.expected_result,
                "expected_alert": definition.expected_alert,
                "random_seed": manifest.random_seed,
                "category": manifest.category,
                "shape_family": definition.settings.shape_family.value,
                "change_type": event.change_type.value if event is not None else None,
                "change_time_ns": (
                    event.first_seen_timestamp_ns if event is not None else None
                ),
                "object_volume_m3": _object_volume_m3(manifest_path),
            }
        )

    index = {
        "schema_version": GOLDEN_PACK_SCHEMA_VERSION,
        "pack_status": GOLDEN_PACK_STATUS,
        "decision_status": GOLDEN_PACK_DECISION_STATUS,
        "scenario_count": len(entries),
        "scenarios": entries,
    }
    (root / "golden-pack.json").write_text(
        json.dumps(index, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    checksums = _sha256_inventory(root)
    (root / "checksums.sha256").write_text(
        "".join(f"{digest}  {path}\n" for path, digest in checksums.items()),
        encoding="utf-8",
        newline="\n",
    )
    return root

"""Frozen evaluation dataset definition and generator for Gate 6."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from kyra.cli import _add_initial_near_track, _compose_timed_track, _make_restock_track_transient
from kyra.contracts import ChangeType
from kyra.manifest import ShapeFamily
from kyra.simulation import ScenarioCondition, ScenarioSettings, generate_scenario

# 20 held-out categories across the 4 shape families (Section 10 of assignment plan)
HELD_OUT_CATEGORIES: dict[ShapeFamily, tuple[str, ...]] = {
    ShapeFamily.THIN_BOX_OR_TRAY: (
        "cereal_box",
        "pasta_box",
        "biscuit_packet",
        "chocolate_bar",
        "tea_box",
    ),
    ShapeFamily.CYLINDER: (
        "soda_can",
        "soup_can",
        "water_bottle",
        "spice_jar",
        "cleaning_spray",
    ),
    ShapeFamily.IRREGULAR: (
        "sneaker",
        "stuffed_toy",
        "hand_soap_pump",
        "fruit_bunch",
        "power_drill",
    ),
    ShapeFamily.HANDLED_OR_HANGING: (
        "mug",
        "kettle",
        "measuring_pitcher",
        "frying_pan",
        "basket",
    ),
}


@dataclass(frozen=True)
class EvaluationScenarioSpec:
    scenario_id: str
    is_positive: bool
    category: str
    shape_family: ShapeFamily
    condition: ScenarioCondition
    change_type: ChangeType | None
    should_alert: bool
    system_mode: str = "NORMAL"
    profile: str = "default"
    seed: int = 1000


def generate_evaluation_specs() -> list[EvaluationScenarioSpec]:
    """Generate all 420 frozen evaluation scenario specifications per Section 10."""
    specs: list[EvaluationScenarioSpec] = []
    base_seed = 5000

    # -------------------------------------------------------------
    # 1. Frozen Positive: 120 removal scenarios
    # -------------------------------------------------------------
    # Group A: 60 procedural held-out scenarios across 20 categories (3 variants each)
    pos_idx = 1
    for shape_family, categories in HELD_OUT_CATEGORIES.items():
        for category in categories:
            for variant in range(3):
                specs.append(
                    EvaluationScenarioSpec(
                        scenario_id=f"frozen-pos-{pos_idx:03d}-{category}-v{variant + 1}",
                        is_positive=True,
                        category=category,
                        shape_family=shape_family,
                        condition=ScenarioCondition.OBJECT_CHANGE,
                        change_type=ChangeType.REMOVAL,
                        should_alert=True,
                        profile="suspicious_removal",
                        seed=base_seed + pos_idx,
                    )
                )
                pos_idx += 1

    # Group B: 60 reversed transitions (real/synthetic unstacked object pairs)
    for rev_idx in range(60):
        # Vary across shape families
        shapes = list(ShapeFamily)
        sf = shapes[rev_idx % len(shapes)]
        specs.append(
            EvaluationScenarioSpec(
                scenario_id=f"frozen-pos-{pos_idx:03d}-reversed-ocid-{rev_idx + 1:02d}",
                is_positive=True,
                category=f"ocid_clutter_item_{rev_idx + 1:02d}",
                shape_family=sf,
                condition=ScenarioCondition.OBJECT_CHANGE,
                change_type=ChangeType.REMOVAL,
                should_alert=True,
                profile="occlusion_then_removal" if rev_idx % 4 == 0 else "suspicious_removal",
                seed=base_seed + pos_idx,
            )
        )
        pos_idx += 1

    # -------------------------------------------------------------
    # 2. Frozen Negative: 300 challenge control trials
    # -------------------------------------------------------------
    neg_idx = 1
    # 75 occlusion-only scenarios
    for i in range(75):
        specs.append(
            EvaluationScenarioSpec(
                scenario_id=f"frozen-neg-{neg_idx:03d}-occlusion-only-{i + 1:02d}",
                is_positive=False,
                category="control_item",
                shape_family=ShapeFamily.THIN_BOX_OR_TRAY,
                condition=ScenarioCondition.PERSON_ONLY_OCCLUSION,
                change_type=None,
                should_alert=False,
                profile="occlusion_only",
                seed=base_seed + 1000 + neg_idx,
            )
        )
        neg_idx += 1

    # 75 nearby-person / no-removal scenarios
    for i in range(75):
        specs.append(
            EvaluationScenarioSpec(
                scenario_id=f"frozen-neg-{neg_idx:03d}-nearby-person-{i + 1:02d}",
                is_positive=False,
                category="control_item",
                shape_family=ShapeFamily.CYLINDER,
                condition=ScenarioCondition.NO_CHANGE,
                change_type=None,
                should_alert=False,
                profile="person_without_removal",
                seed=base_seed + 1000 + neg_idx,
            )
        )
        neg_idx += 1

    # 75 addition or authorized-restocking scenarios
    for i in range(75):
        is_restock = i % 2 == 0
        specs.append(
            EvaluationScenarioSpec(
                scenario_id=f"frozen-neg-{neg_idx:03d}-addition-restock-{i + 1:02d}",
                is_positive=False,
                category="restocked_item",
                shape_family=ShapeFamily.IRREGULAR,
                condition=ScenarioCondition.OBJECT_CHANGE,
                change_type=ChangeType.ADDITION,
                should_alert=False,
                system_mode="RESTOCK_MODE" if is_restock else "NORMAL",
                profile="authorized_restock" if is_restock else "addition",
                seed=base_seed + 1000 + neg_idx,
            )
        )
        neg_idx += 1

    # 75 lighting, drift, invalid-depth or static no-change scenarios
    conditions = [
        (ScenarioCondition.LIGHTING_VARIATION, "lighting"),
        (ScenarioCondition.CAMERA_DRIFT, "camera_drift"),
        (ScenarioCondition.INVALID_DEPTH, "invalid_depth"),
        (ScenarioCondition.NO_CHANGE, "static_no_change"),
    ]
    for i in range(75):
        cond, name = conditions[i % len(conditions)]
        specs.append(
            EvaluationScenarioSpec(
                scenario_id=f"frozen-neg-{neg_idx:03d}-{name}-{i + 1:02d}",
                is_positive=False,
                category="control_item",
                shape_family=ShapeFamily.HANDLED_OR_HANGING,
                condition=cond,
                change_type=None,
                should_alert=False,
                profile=name,
                seed=base_seed + 1000 + neg_idx,
            )
        )
        neg_idx += 1

    return specs


def materialize_scenario(spec: EvaluationScenarioSpec, destination: Path) -> Path:
    """Materialize a scenario on disk from its specification."""
    settings = ScenarioSettings(
        scenario_id=spec.scenario_id,
        random_seed=spec.seed,
        category=spec.category,
        shape_family=spec.shape_family,
        change_type=spec.change_type,
        should_alert=spec.should_alert,
        condition=spec.condition,
        system_mode=spec.system_mode,
        held_out_category=True,
        split="frozen_test",
        baseline_frame_count=30,
        event_frame_count=9 if spec.profile == "occlusion_then_removal" else 7,
    )
    manifest_path = generate_scenario(destination, settings)

    # Compose tracks and profile timing
    if spec.profile == "suspicious_removal":
        _add_initial_near_track(manifest_path)
    elif spec.profile == "person_without_removal":
        _add_initial_near_track(manifest_path)
    elif spec.profile == "authorized_restock":
        _make_restock_track_transient(manifest_path)
    elif spec.profile == "occlusion_then_removal":
        _compose_timed_track(
            manifest_path,
            unchanged_event_frames=2,
            profile="temporary_occlusion_then_removal",
            occlude_object_region=True,
        )
    return manifest_path

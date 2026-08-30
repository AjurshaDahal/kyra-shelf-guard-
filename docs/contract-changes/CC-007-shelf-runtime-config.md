# CC-007 — Shelf configuration boundary

- **Status:** Approved and frozen v1 as of 2026-08-30.
- **Purpose:** Formalize the existing shelf configuration boundary without creating a second parallel runtime configuration model.
- **Repository fact:** The live repository already contains the runtime object `ShelfConfig` in [src/kyra/contracts.py](../../src/kyra/contracts.py#L52-L79) and the persisted representation `ShelfConfigRecord` under `ScenarioManifest.shelf` in [src/kyra/manifest.py](../../src/kyra/manifest.py#L24-L89).
- **Core rule:** This proposal does not create a second `RuntimeConfig` class or duplicate the existing configuration model.

## Approval record

- **Person 1 — Approve** — 2026-08-30 — The five-field shelf boundary matches the scenario and baseline assumptions for persisted shelf geometry.
- **Person 2 — Approve** — 2026-08-30 — The geometry semantics of `roi_xyxy`, `bounds_min_m`, `bounds_max_m`, and `voxel_size_m` are the correct shared boundary.
- **Person 3 — Approve** — 2026-08-30 — No alert or tracking thresholds are being silently absorbed into the C-007 shelf boundary.
- **Person 4 — Approve** — 2026-08-30 — The five-field boundary is the canonical shared runtime/persisted shelf contract and no second configuration model is introduced.

## 1. Problem being solved

The repository already has an operational shelf geometry boundary in two places:

- runtime object: `ShelfConfig` in [src/kyra/contracts.py](../../src/kyra/contracts.py#L52-L79)
- persisted object: `ShelfConfigRecord` / `ScenarioManifest.shelf` in [src/kyra/manifest.py](../../src/kyra/manifest.py#L24-L89)

The problem is not that the boundary does not exist. The problem is that it is not yet formally named, frozen, and approved as the C-007 shared contract. Without that explicit boundary, the project risks silently broadening the shared contract beyond the actual shelf geometry boundary.

This document reconciles the current repository state with the approved architecture:

- C-007 formalizes the existing shelf configuration boundary.
- It does not introduce a second parallel `RuntimeConfig`.
- It does not absorb manifest-level knobs or algorithm-tuning parameters that are not part of the core shelf geometry boundary.

## 2. C-007 v1 scope

C-007 v1 formalizes only the existing shared shelf boundary that already exists in both the runtime and persisted representations:

- `shelf_id`
- `roi_xyxy`
- `bounds_min_m`
- `bounds_max_m`
- `voxel_size_m`

This is the minimal approved boundary. It is intentionally narrow and aligned with the actual repository evidence.

## 3. Exact five-field boundary

The approved C-007 v1 field set is exactly:

- `shelf_id: str`
- `roi_xyxy: tuple[int, int, int, int]`
- `bounds_min_m: tuple[float, float, float]`
- `bounds_max_m: tuple[float, float, float]`
- `voxel_size_m: float`

This boundary matches the existing implementation in both [src/kyra/contracts.py](../../src/kyra/contracts.py#L52-L79) and [src/kyra/manifest.py](../../src/kyra/manifest.py#L24-L39).

## 4. Runtime representation

`ShelfConfig` remains the canonical runtime representation.

It is already defined at [src/kyra/contracts.py](../../src/kyra/contracts.py#L52-L79) and already validates:

- ROI width and height are positive
- 3-D shelf bounds have positive extent
- voxel size is positive

This runtime object is not replaced by a second `RuntimeConfig` class. No duplicate representation is introduced.

## 5. Persisted representation

`ShelfConfigRecord` remains the persisted representation, and `ScenarioManifest.shelf` remains the persisted C-007 boundary.

The live persisted model is defined in [src/kyra/manifest.py](../../src/kyra/manifest.py#L24-L39) and used by `ScenarioManifest` in [src/kyra/manifest.py](../../src/kyra/manifest.py#L67-L89).

This persisted contract intentionally mirrors the same five-field boundary exactly.

## 6. Relationship between runtime and persisted representations

The relationship is:

- `ShelfConfig` = runtime representation of the shared shelf boundary
- `ShelfConfigRecord` = serialized JSON representation for the same boundary
- `ScenarioManifest.shelf` = the persisted manifestation of the same C-007 boundary inside the versioned scenario manifest

There is no second configuration model and no duplication of the same concept under a second class name.

The contract boundary is one semantic concept with two representations:

- in memory: `ShelfConfig`
- on disk: `ShelfConfigRecord` / `ScenarioManifest.shelf`

## 7. Explicitly excluded fields

The following existing fields remain explicitly outside C-007 unless an owner-approved future proposal says otherwise:

- `random_seed` — current manifest field in [src/kyra/manifest.py](../../src/kyra/manifest.py#L67-L94)
- `system_mode` — current manifest field in [src/kyra/manifest.py](../../src/kyra/manifest.py#L67-L94)
- `intrinsics` — required calibration data in [src/kyra/contracts.py](../../src/kyra/contracts.py#L81-L150)
- `camera_to_shelf` — required calibration transform in [src/kyra/contracts.py](../../src/kyra/contracts.py#L81-L150)
- `portable_max_volume_m3`
- `removal_floor_m`
- `registration_reject_m`
- `minimum_visible_fraction`
- `minimum_alert_volume_m3`
- `proximity_distance_m`

Reason for exclusion:

These values exist in the current `ShelfConfig` dataclass, but the repository does not currently prove they are part of the formal shared shelf boundary. They read as geometry or algorithm-tuning parameters rather than the canonical shelf geometry contract. They are not automatically promoted into C-007.

## 8. No-duplicate-configuration rule

This proposal explicitly rejects any second runtime configuration model.

The approved architecture is:

- no `RuntimeConfig` class
- no duplicate config schema
- no parallel shelf config object for runtime and persisted data
- no “config runtime model” that diverges from the existing `ShelfConfig`

This proposal is a formalization of the existing boundary, not a redesign of the configuration layer.

## 9. Versioning and compatibility approach

C-007 must follow the repository’s existing versioning conventions rather than inventing a separate incompatible system.

Repository conventions already in use:

- manifest versioning in [src/kyra/manifest.py](../../src/kyra/manifest.py#L15-L18)
- supported-version validation and rejection in [src/kyra/manifest.py](../../src/kyra/manifest.py#L90-L125)
- canonical JSON serialization and checksum behavior in [src/kyra/manifest.py](../../src/kyra/manifest.py#L99-L133)
- contract-change approval flow in [docs/CONTRACT_CHANGE_PROCESS.md](../CONTRACT_CHANGE_PROCESS.md#L1-L38)

C-007 v1 should therefore:

- use the existing manifest versioning pattern for any persisted scenario change
- keep the runtime `SCHEMA_VERSION` in [src/kyra/contracts.py](../../src/kyra/contracts.py#L13-L16) unchanged unless a separate approved runtime-contract change is intentionally made
- treat `ScenarioManifest.shelf` as the persisted representation of the C-007 boundary
- reject unsupported or silently reinterpreted field sets as a fail-closed contract change

This preserves the project’s existing compatibility model and avoids creating a second incompatible contract system.

## 10. Validation requirements

Before implementation is approved, the proposal must validate the following:

- the five-field boundary is identical in runtime and persisted forms
- the runtime `ShelfConfig` continues to validate ROI and bound extents correctly
- the persisted `ShelfConfigRecord` accepts exactly the same five fields
- unsupported extra fields are rejected by strict model validation
- no manifest-level fields such as `random_seed`, `system_mode`, `intrinsics`, or `camera_to_shelf` are silently included in C-007
- the five-field boundary preserves the repository’s canonical serialization and compatibility strategy

This requirement uses the existing validation pattern already present in [src/kyra/contracts.py](../../src/kyra/contracts.py#L52-L79) and [src/kyra/manifest.py](../../src/kyra/manifest.py#L90-L125).

## 11. Serialization requirements

Persisted C-007 data must remain a normal manifest field:

- `ScenarioManifest.shelf` contains the serialized `ShelfConfigRecord`
- the field order and canonical JSON behavior remain under the existing manifest serialization path in [src/kyra/manifest.py](../../src/kyra/manifest.py#L99-L133)
- no independent JSON schema is introduced for a parallel runtime config object

This is consistent with the project’s existing storage model described in [docs/DECISIONS.md](../DECISIONS.md#L25-L57).

## 12. Compatibility requirements

C-007 must obey the repository’s compatibility policy in [docs/CONTRACT_CHANGE_PROCESS.md](../CONTRACT_CHANGE_PROCESS.md#L1-L38):

- propose before implementation
- list all affected owners, producers, consumers, and tests
- clearly state old/new field semantics and version effects
- preserve backward compatibility unless a versioned change is explicitly approved
- fail closed on unknown or invalid values
- no silent reinterpretation of stored shelf data

Because this proposal formalizes an existing boundary, the compatibility burden is reduced: it is a contract clarification, not a new runtime model.

## 13. Affected owners and review requirements

Affected owners:

- Person 4: accountable for the shared contract and gate evidence
- Person 1: scenario data and shelf calibration assumptions
- Person 2: geometry consumers of the shelf boundary
- Person 3: any consumer of shelf state or alert/proximity thresholds if they are later declared shared

Required review:

- Person 4 must confirm the contract registry entry
- Person 1 must confirm the persisted shelf boundary matches scenario/baseline assumptions
- Person 2 must confirm the geometry semantics of `roi_xyxy`, `bounds_min_m`, `bounds_max_m`, and `voxel_size_m`
- Person 3 must confirm no tracking or alert thresholds are being silently absorbed into C-007

Silence is not approval.

## 14. Gate 1 relevance

This proposal directly addresses the “shelf/configuration” component of Gate 1 in [docs/INTEGRATION_GATES.md](../INTEGRATION_GATES.md#L5-L13).

It does not claim Gate 1 is closed. It states the approved architectural answer:

- the shared shelf/configuration boundary is already represented by `ShelfConfig` and `ScenarioManifest.shelf`
- C-007 is the formalization of that existing boundary
- the gate criterion is satisfied only after explicit owner approval and evidence

## 15. Exact implementation scope AFTER this design is approved

Only after explicit approval, the implementation scope will be limited to:

- formalizing the C-007 contract registry entry and documentation
- ensuring `ShelfConfig` and `ShelfConfigRecord` remain aligned to the five-field boundary
- adding or adjusting tests that validate the boundary is the same in runtime and persisted forms
- ensuring no second runtime config model is introduced

The following remain intentionally out of scope:

- no second `RuntimeConfig` class
- no C-008
- no source-code changes to Person 1, Person 2, or Person 3 algorithms
- no pipeline implementation
- no broadening of C-007 beyond the five approved fields

## Final design conclusion

C-007 is not a new runtime config architecture. It is a formalization of the live shelf configuration boundary already represented by:

- `ShelfConfig` in [src/kyra/contracts.py](../../src/kyra/contracts.py#L52-L79)
- `ShelfConfigRecord` / `ScenarioManifest.shelf` in [src/kyra/manifest.py](../../src/kyra/manifest.py#L24-L89)

The approved C-007 v1 boundary is exactly:

- `shelf_id`
- `roi_xyxy`
- `bounds_min_m`
- `bounds_max_m`
- `voxel_size_m`

Everything else remains outside C-007 until a separate, explicit owner-approved contract change proves it belongs there.

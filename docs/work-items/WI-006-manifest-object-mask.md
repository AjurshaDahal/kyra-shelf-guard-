# WI-006 — Manifest object-mask compatibility and reader support

- **Owner:** P1
- **Status:** Complete
- **Started:** 2026-08-30
- **Completed:** 2026-08-30
- **Requirements:** P-005 / C-006, P1-IO-004, P1-SIM-004
- **Integration gate:** Gate 1

## Objective

Implement the approved object-mask/shape-family manifest extension without changing the shared runtime contract for `FramePacket` or the runtime `SCHEMA_VERSION`.

## In scope

- Manifest versioning support for 1.0 and 1.1 in `src/kyra/manifest.py`.
- `FrameRecord.object_mask_path` and `GroundTruthEvent.shape_family` support.
- Validation for unsupported versions, missing `shape_family`, and missing `object_mask_path` in version 1.1 scenarios.
- `ScenarioFrameSource.object_mask(frame_id)` in `src/kyra/io.py` with dimension checks and the same asset path safety as other mask readers.
- Implementation and regression tests covering version compatibility, manifest validation, and object-mask replay behavior.

## Out of scope

- Runtime `FramePacket` changes.
- Changes to `src/kyra/contracts.py` or any other runtime contract dataclass.
- Person 2 geometry, Person 3 tracking/rules, pipeline, CLI, evaluation, benchmarking, or T4 validation.
- New design work beyond the approved P-005 manifest object-metadata extension.

## Inputs, outputs, and contracts

- Shared runtime contract remains frozen at `SCHEMA_VERSION = "1.0"` in `src/kyra/contracts.py`.
- Manifest schema uses `MANIFEST_SCHEMA_VERSION = "1.1"` with supported versions `{"1.0", "1.1"}`.
- New manifest writes use version 1.1; version 1.0 remains readable.
- `FrameRecord.object_mask_path` is a relative string or `None` for compatibility/no-object cases.
- `GroundTruthEvent.shape_family` uses the approved values: `thin_box_or_tray`, `cylinder`, `irregular`, and `handled_or_hanging`.
- `ScenarioFrameSource.object_mask(frame_id)` returns a boolean array with depth shape and all-false fallback when no mask is present.
- Person 2 and Person 3 were both confirmed "Not affected" for P-005 on 2026-08-30.

## Implementation summary

Implemented the approved C-006 manifest extension and object-mask reader support while leaving the shared runtime contract untouched. The manifest now accepts both 1.0 and 1.1, rejects unsupported version strings, validates version 1.1 object metadata, and writes 1.1. The replay reader adds `object_mask(frame_id)` with correct missing-mask fallback and strict dimension checks, consistent with the repository’s existing path and mask safety rules.

## Documentation impact

- Updated Person 1 status to reflect the approved manifest implementation.
- Updated Person 4 status to reflect Person 4-owned shared-contract completion.
- Updated the changelog for the manifest extension landing.
- Updated the shared contract registry and decision record to reflect implemented P-005/C-006 status.
- Added this work-item record for durable implementation history.

## Verification

| Environment | Command | Result | Evidence |
|---|---|---|---|
| Windows, Python 3.12 | `.venv\Scripts\python.exe -m pytest tests/test_manifest.py tests/test_io.py -q` | Passed | 26 passed in 0.41s |
| Windows, Python 3.12 | `.venv\Scripts\python.exe -m pytest -q` | Passed | 62 passed in 0.64s |
| Windows, repository | `.venv\Scripts\python.exe scripts\check_repo_consistency.py` | Passed | Repository consistency validation passed |
| Windows, repository | `.venv\Scripts\python.exe scripts\check_change_impact.py --base HEAD` | Passed | Change-impact validation passed after governance sync |
| Windows, repository | `git diff --check` | Passed | No whitespace or diff-format errors |

## Risks, limitations, and failures

The implementation remains intentionally narrow: this work does not include Person 2 geometry, Person 3 tracking rules, pipeline/evaluation, or any runtime contract expansion. No additional approval was required beyond the committed P-005 approval because the design and approval record already existed.

## Handoff

The manifest and replay contract for C-006 is complete and synchronized with repository governance. The next Person 4 task is to continue the remaining Gate 1 contract work and evaluation/pipeline milestones, without broadening the runtime schema or the P-005 manifest design.

## Final links

- Issue: N/A
- Pull request: N/A
- Commit: N/A

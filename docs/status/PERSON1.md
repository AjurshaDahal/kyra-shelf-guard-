# Person 1 Status — Data and Baseline

- **Status:** In progress
- **Last updated:** 2026-08-24

## Implemented

- Foundation shared data objects and strict scenario manifest/checksum behavior.
- Replayable RGB/depth/mask input with malformed-file checks and defensive track-annotation access.
- Thirty-frame baseline construction, save/load/checksum behavior, and MiDaS metric-anchor alignment policy.
- Approved P-005 manifest extension for versioned object metadata: `object_mask_path`, `shape_family`, and `ScenarioFrameSource.object_mask(frame_id)`.
- C-006 manifest validation and reader support for version 1.0/1.1 compatibility, unsupported-version rejection, and object-mask dimension/path safety checks.

## Active

- The approved P-005/C-006 manifest contract is implemented and validated in the current branch.
- The next Person 1 work remains the deterministic generator, ten-scenario golden pack, OCID converter/provenance, target-T4 check, and independent handoff.

## Blocked or pending

- Deterministic generator, ten-scenario golden pack, OCID converter/provenance, target-T4 check, and independent handoff remain unimplemented.

## Next

Continue the Person 1 implementation plan after the approved manifest contract lands. Do not broaden the shared schema beyond the approved P-005/C-006 scope.

## Evidence

- Baseline commit `2b4dbba`.
- Windows/Python 3.12.7: `python -m pytest` — 35 passed on 2026-08-24.
- Windows/Python 3.12.7: `python -m ruff check .` — passed on 2026-08-24.
- Current C-006 governance validation on 2026-08-30: `python -m pytest tests/test_manifest.py tests/test_io.py -q` — 26 passed.
- Current C-006 governance validation on 2026-08-30: `python -m pytest -q` — 62 passed.
- This evidence covers the manifest and replay contract implementation; it is not golden-pack, target-T4, or end-to-end proof.

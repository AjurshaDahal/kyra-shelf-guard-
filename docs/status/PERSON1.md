# Person 1 Status — Data and Baseline

- **Status:** In progress
- **Last updated:** 2026-08-24

## Implemented

- Foundation shared data objects and strict scenario manifest/checksum behavior.
- Replayable RGB/depth/mask input with malformed-file checks and defensive track-annotation access.
- Thirty-frame baseline construction, save/load/checksum behavior, and MiDaS metric-anchor alignment policy.

## Active

- No implementation work item is currently claimed in this repository snapshot.

## Blocked or pending

- P-001 package layout decision.
- P-005 manifest object-mask and shape-family proposal approval.
- Deterministic generator, ten-scenario golden pack, OCID converter/provenance, target-T4 check, and independent handoff remain unimplemented.

## Next

Claim the next ordered task in `../PERSON1_IMPLEMENTATION_PLAN.md`, confirm it does not depend on P-005, and implement it with deterministic acceptance evidence.

## Evidence

- Baseline commit `2b4dbba`.
- Windows/Python 3.12.7: `python -m pytest` — 35 passed on 2026-08-24.
- Windows/Python 3.12.7: `python -m ruff check .` — passed on 2026-08-24.
- This evidence is local foundation evidence only; it is not golden-pack, target-T4, or end-to-end proof.

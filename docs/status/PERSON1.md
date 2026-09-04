# Person 1 Status — Data and Baseline

- **Status:** In progress
- **Last updated:** 2026-09-05

## Implemented

- Foundation shared data objects and strict scenario manifest/checksum behavior.
- Replayable RGB/depth/mask input with malformed-file checks and defensive track-annotation access.
- Thirty-frame baseline construction, save/load/checksum behavior, and MiDaS metric-anchor alignment policy.
- Approved P-005 manifest extension for versioned object metadata: `object_mask_path`, `shape_family`, and `ScenarioFrameSource.object_mask(frame_id)`.
- C-006 manifest validation and reader support for version 1.0/1.1 compatibility, unsupported-version rejection, and object-mask dimension/path safety checks.
- P1-03 lightweight deterministic scenario generation for removal and addition
  events, including 30 baseline frames, lossless RGB/depth/mask assets, all four
  approved shape families, and synthetic ground-truth metadata.

## Active

- P1-03 is in review under issue #14 and pull request #16. Its focused tests
  cover replay, same-seed bytes and file hashes, different-seed assets,
  addition/removal state, path portability, shape coverage, and refusal to
  overwrite non-empty output.
- The next Person 1 work is P1-04: confirm the provisional tenth-scenario choice,
  then compose and audit the ten-scenario golden pack from the generator.

## Blocked or pending

- Ten-scenario golden pack, OCID converter/provenance, target-T4 check, and
  independent handoff remain unimplemented.
- The golden pack cannot be called frozen until the team confirms the
  provisional second-removal interpretation for scenario ten.

## Next

Review P1-03 without broadening C-006/C-007, then claim P1-04 and record the
team's scenario-ten decision before freezing golden checksums.

## Evidence

- Baseline commit `2b4dbba`.
- Windows/Python 3.12.7: `python -m pytest` — 35 passed on 2026-08-24.
- Windows/Python 3.12.7: `python -m ruff check .` — passed on 2026-08-24.
- Current C-006 governance validation on 2026-08-30: `python -m pytest tests/test_manifest.py tests/test_io.py -q` — 26 passed.
- Current C-006 governance validation on 2026-08-30: `python -m pytest -q` — 62 passed.
- P1-03 focused validation on current `origin/main` integration on 2026-09-05:
  `python -m pytest tests/test_simulation.py -q` — 8 passed in 4.27s.
- P1-03 full validation on Windows/Python 3.12.7 on 2026-09-05:
  113 tests passed in 4.64s; Ruff, byte-compilation, repository consistency, and
  change-impact validation passed.
- The P1-03 evidence is synthetic and local. It does not prove the golden pack,
  target T4, public-data conversion, Gate 2 completion, or end-to-end behavior.

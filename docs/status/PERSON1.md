# Person 1 Status — Data and Baseline

- **Status:** In progress
- **Last updated:** 2026-09-06

## Implemented

- Foundation shared data objects and strict scenario manifest/checksum behavior.
- Replayable RGB/depth/mask input with malformed-file checks and defensive track-annotation access.
- Thirty-frame baseline construction, save/load/checksum behavior, and MiDaS metric-anchor alignment policy.
- Approved P-005 manifest extension for versioned object metadata: `object_mask_path`, `shape_family`, and `ScenarioFrameSource.object_mask(frame_id)`.
- C-006 manifest validation and reader support for version 1.0/1.1 compatibility, unsupported-version rejection, and object-mask dimension/path safety checks.
- P1-03 lightweight deterministic scenario generation for removal and addition
  events, including 30 baseline frames, lossless RGB/depth/mask assets, all four
  approved shape families, and synthetic ground-truth metadata. Merged as `71c1416`.
- P1-04 candidate composition of ten tiny deterministic scenarios covering the
  reviewed behavior matrix and all four shape families, with portable manifest
  paths, SHA-256 inventory, and byte-identical regeneration checks.
- P1-06 baseline calibration hardening on 2026-09-06 (WI-021): mixed-resolution
  and changed-intrinsics batches reject, unsafe occupancy-grid dimensions
  reject, empty-shelf all-fixed geometry with zero portable components, noise
  sigma tracking under injected jitter, checksum stability/sensitivity and
  documented single-frame-outlier absorption, and fixed/portable pixel
  separation evidence.
- P1-07 known-volume acceptance suite on 2026-09-06 (WI-021): seven
  parametrized cases (boxes, cylinders, irregular L union; 0.55-1.72 litres;
  varied positions and top depths) all within the 10% volume bound, plus a
  hanging-plate guard case recording the expected void-column overestimate.
- P1-08 MiDaS alignment policy matrix on 2026-09-06 (WI-021): approximate-flag
  labeling for MIDAS_ALIGNED sources, round-trip persistence of the flag,
  valid-only (zero-for-unknown) aligned output, and an explicit, enforceable
  residual limit.

## Active

- P1-04 is locally implemented under issue #17 on branch
  `p1/17-golden-scenario-pack`, now integrated with the P1-03 merge on current
  `origin/main`. The candidate uses the D-009 provisional irregular-item
  removal as G03 and remains unfrozen.
- P1-06/P1-07/P1-08 are implemented under issue #21 on branch
  `p1/21-calibration-baseline-acceptance`; pull request #22 is open for review.
  The
  MiDaS policy tests stay in `tests/test_baseline.py` because the current
  change-impact classifier (issue #18) would misclassify the plan-named
  `tests/test_midas_alignment.py` as Person 4; the deviation is recorded in
  the plan and in WI-021.
- Handled/hanging overhang objects remain a documented known-bias case: the
  baseline estimator integrates the void column under a hanging object, so
  those cases exceed the 10% acceptance bound by design and belong to Person
  2's occlusion-safe geometry scope.

## Blocked or pending

- Team-confirmed frozen checksums, OCID converter/provenance, target-T4 check,
  and independent handoff remain unimplemented.
- The golden pack cannot be called frozen until the team confirms the
  provisional second-removal interpretation for scenario ten (D-009).
- Issue #18 blocks pushing P1-04: the authoritative P1 plan and ownership matrix
  assign the named golden-pack script and test to Person 1, but the current
  change-impact classifier assigns both paths to Person 4 and treats the script
  as governance. Person 4 must approve and land the narrow classifier fix.

## Next

- Let Person 4 resolve issue #18, then merge that governance fix into the
  clean `p1/17` issue branch, rerun every gate, push the candidate for review,
  and record the team's D-009 choice before changing its status or treating
  its checksums as frozen evidence.
- Review and merge `p1/21-calibration-baseline-acceptance` (WI-021), then
  proceed to P1-09 provenance and P1-10 OCID converter.

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
  change-impact validation passed. Pull request #16 then merged as `71c1416`.
- P1-04 focused validation on current `origin/main` integration on 2026-09-05:
  `python -m pytest tests/test_simulation.py tests/test_golden_pack.py -q`
  — 11 passed in 6.46s. The 117-file candidate is 62,614 bytes and regenerates
  to the same recorded SHA-256 inventory.
- P1-04 full validation on Windows/Python 3.12.7 on 2026-09-05:
  116 tests passed in 5.58s; Ruff, byte-compilation, and repository consistency
  passed.
- P1-04 change-impact validation against `origin/main` failed on 2026-09-05
  because the classifier requires Person 4 status and
  governance-document changes for the explicitly P1-owned script/test paths.
  The conflict is recorded in issue #18; no false companion edits were added.
- P1-06/P1-07/P1-08 focused validation on 2026-09-06:
  `python -m pytest tests/test_baseline.py tests/acceptance/test_baseline_volume.py -q`
  — 31 passed in 0.23s.
- P1-06/P1-07/P1-08 full validation on Windows/Python 3.12.7 on 2026-09-06:
  134 tests passed in 3.25s; Ruff, byte-compilation, repository consistency,
  and change-impact validation against `origin/main` passed on a clean
  `p1/21` branch with the required companions.
- The P1-03/P1-04/P1-06/P1-07/P1-08 evidence is synthetic and local. It does
  not freeze D-009, prove target T4 portability, run downstream detection,
  close Gate 2, or establish real end-to-end behavior.
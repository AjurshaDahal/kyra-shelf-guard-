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
- P1-06 baseline calibration hardening (WI-021): mixed-resolution and
  changed-intrinsics batches reject, unsafe occupancy-grid dimensions reject,
  empty-shelf all-fixed geometry with zero portable components, noise sigma
  tracking under injected jitter, checksum stability/sensitivity and documented
  single-frame-outlier absorption, and fixed/portable pixel separation evidence.
- P1-07 known-volume acceptance suite (WI-021): seven parametrized cases (boxes,
  cylinders, irregular L union; 0.55-1.72 litres; varied positions and top
  depths) all within the 10% volume bound, plus a hanging-plate guard case
  recording the expected void-column overestimate.
- P1-08 MiDaS alignment policy matrix (WI-021): approximate-flag labeling for
  MIDAS_ALIGNED sources, round-trip persistence of the flag, valid-only
  (zero-for-unknown) aligned output, and an explicit, enforceable residual
  limit.
- P1-09 provenance record on 2026-09-06 (WI-023): `data-sources/provenance.json`
  and `data-sources/README.md` with the `docs/DATASETS.md` field set, a schema
  test that rejects missing licence, checksum, selection, or exclusion
  information, and honest `pending_download` status for OCID.
- P1-10 OCID conversion mapping on 2026-09-06 (WI-023): `src/kyra/ocid.py`
  parses OCID-style metadata strictly, maps depth to uint16 millimetres while
  keeping zero unknown, derives windowed addition/removal events, reverses a
  valid addition into a removal with re-created monotonic timestamps and
  last-seen object-mask semantics, gates the source by SHA-256, and is replayed
  through the manifest 1.1 reader on the tiny committed `tests/fixtures/ocid-mini/`.

## Active

- P1-04 is locally implemented under issue #17 on branch
  `p1/17-golden-scenario-pack`, now integrated with the P1-03 merge on current
  `origin/main`. The candidate uses the D-009 provisional irregular-item
  removal as G03 and remains unfrozen.
- P1-06/P1-07/P1-08 are implemented under issue #21; pull request #22 merged
  as `ca8715c`.
- P1-09/P1-10 are implemented under issue #23; pull request #24 merged as
  `c7de178`. `scripts/convert_ocid.py` is
  implemented locally but stays out of the push while issue #18 keeps every
  `scripts/*.py` change classified as Person 4/governance; the plan-named
  `tests/test_provenance.py` is delivered as `tests/test_dataset_provenance.py`
  for the same reason (both deviations recorded in WI-023 and the plan).
- Handled/hanging overhang objects remain a documented known-bias case: the
  baseline estimator integrates the void column under a hanging object, so
  those cases exceed the 10% acceptance bound by design and belong to Person
  2's occlusion-safe geometry scope.

## Blocked or pending

- Team-confirmed frozen checksums, real OCID download/conversion, target-T4
  check, and independent handoff remain unimplemented.
- The golden pack cannot be called frozen until the team confirms the
  provisional second-removal interpretation for scenario ten (D-009).
- Issue #18 blocks pushing P1-04's golden-pack script/tests and
  `scripts/convert_ocid.py`: the change-impact classifier assigns those paths
  to Person 4. Person 4 must approve and land the narrow classifier fix.

## Next

- Let Person 4 resolve issue #18, then merge that governance fix into the
  clean `p1/17` issue branch and push the golden-pack candidate for review.
- Push `p1/17` and `p1/25` once issue #18 lands, then proceed to P1-12/P1-13
  validation and handoff.

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
- P1-09/P1-10 focused validation on 2026-09-06:
  `python -m pytest tests/test_ocid.py tests/test_dataset_provenance.py -q`
  — 21 passed in 0.41s.
- P1-09/P1-10 script smoke check on 2026-09-06:
  `python scripts/convert_ocid.py ... --reverse` (local, not pushed) exited 0,
  replayed the reversed removal through `ScenarioFrameSource`, and a tampered
  checksum was rejected with exit 2.
- The P1-03/P1-04/P1-06/P1-07/P1-08/P1-09/P1-10 evidence is synthetic and
  local. It does not freeze D-009, prove target T4 portability, run downstream
  detection, close Gate 2, or establish real end-to-end behavior.
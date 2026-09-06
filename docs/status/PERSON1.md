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
- P1-11 single verification entry point on 2026-09-06 (WI-025):
  `scripts/verify_person1.py` runs schema, golden-checksum, reader, baseline,
  MiDaS-policy, and provenance checks with clear collected failure messages,
  canonical-LF text-asset hashing (Windows CRLF and T4 LF trees verify
  identically), and honest non-vacuous failure when the pack or provenance
  record is absent.
- P1-12 Windows candidate-leg report on 2026-09-06:
  `docs/PERSON1_TEST_REPORT_WINDOWS_CANDIDATE.md` records environment
  identity, exact commands with exits and durations, acceptance rows, and all
  G01-G10 loads for the candidate pack on the merged `p1/17` tree (158 tests
  passed; the seven-check verifier exited 0). The target-T4 leg remains
  blocked on G0.4 and the D-009 freeze decision; the local RTX 2050 machine is
  not target-T4 evidence.
- P1-13 handoff package prepared on 2026-09-06 (`docs/PERSON1_HANDOFF.md`):
  exact reproducible commands with their recorded outputs (setup, 161 tests,
  seven-check verifier, golden regeneration byte-identity, OCID smoke with
  tamper gate, baseline/volume, lint and consistency), a limitations section,
  and an independent-teammate sign-off block. The three blocking decisions
  (D-009, P-003, G0.4) are consolidated under issue #40.

## Active

- P1-04 candidate golden pack merged via pull request #27 as `327a905`. The
  candidate uses the D-009 provisional irregular-item removal as G03 and
  remains unfrozen until the team confirms scenario ten.
- P1-11 verification entry point merged via pull request #28 as `7f2fd84`.
- P1-06/P1-07/P1-08 are implemented under issue #21; pull request #22 merged
  as `ca8715c`.
- P1-09/P1-10 are implemented under issue #23; pull request #24 merged as
  `c7de178`, and the OCID conversion CLI `scripts/convert_ocid.py` merged via
  pull request as part of WI-031 (the issue #18 classifier fix, `0b034c0`,
  unblocked its push).
- Handled/hanging overhang objects remain a documented known-bias case: the
  baseline estimator integrates the void column under a hanging object, so
  those cases exceed the 10% acceptance bound by design and belong to Person
  2's occlusion-safe geometry scope.

## Blocked or pending

- D-009 team confirmation (issue #40) is required before the pack checksums
  can be frozen; only then can the target-T4 leg use frozen checksums and the
  independent handoff be completed.
- Real OCID download/conversion remains blocked on the P-003 licence review
  (issue #40).
- Target-T4 check and independent handoff are prepared but not yet executed
  (G0.4 assignment and an independent teammate respectively).

## Next

- The team resolves issue #40 (D-009, P-003, G0.4) so the pack can be frozen,
  the T4 leg run, and the P1-13 handoff guide executed by an independent
  teammate.

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
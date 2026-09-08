# Person 1 Status — Data and Baseline

- **Status:** Complete
- **Last updated:** 2026-09-08

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
  (D-009, P-003, G0.4) were resolved via issue #56 and closed issue #40.
- P1-14 target-T4 leg executed on 2026-09-07 on the Kaggle free-T4 GPU
  notebook (issue #64): report `docs/PERSON1_TEST_REPORT_T4_2026-09-07.md`
  records 189 tests passed in 1.95s, `verify_person1.py` exit 0, byte-identical
  golden-pack regeneration audit (116/116, re-verified locally), and the
  optional GPU published-pin smoke (probe exit 0) on snapshot
  `main` `65d3707`; limitations (runner-confirmed accelerator identity,
  no independent sign-off) are recorded in the report.
- P1-15 real MiDaS adapter work completed locally (issue #84): lazy loading from the official
  v3.1 repository commit, source-resolution finite float32 relative inverse
  depth, clear optional-dependency/device failures, and the upstream-compatible
  `timm==0.6.13` pin. Four independent OCID source sequences produced finite
  480x640 float32 maps on CPU; the report is retained externally with hashes.
  The two-anchor aligned maps are functional approximate-metric smokes, not an
  independent accuracy test. This does not establish latency, live-camera
  behavior, metric accuracy, volume accuracy, or an alert result.
- P1-15 real OCID recorded-data smoke on 2026-09-08 (GitHub issue #81): the
  6,822,716,319-byte OCID 1.0.0 archive matched the publisher MD5 and the
  recorded local SHA-256. Four ARID20 tabletop sequences were converted in
  forward and reverse order; all 8 manifests and 168 frames replayed through
  `ScenarioFrameSource` with monotonic timestamps, matching image dimensions,
  `float32` metric depth, and zero preserved as unknown.

## Active

- P1-15 implementation and bounded four-sequence CPU smoke are complete on the
  working branch under issue #84; pull-request review remains. Generated maps
  and model weights remain outside Git.
- P1-04 candidate golden pack merged via pull request #27 as `327a905`, and
  frozen on 2026-09-06 after the D-009 confirmation: `golden-pack.json`
  records `pack_status: frozen` and `decision_status: D-009-confirmed-2026-09-06`.
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

- The target-T4 leg was executed on 2026-09-07 on a Kaggle free-T4 GPU notebook (D-015) with the frozen `main` `65d3707` snapshot; the dated report is `docs/PERSON1_TEST_REPORT_T4_2026-09-07.md` (189 passed, verifier exit 0, golden pack byte-identical). The accelerator identity is runner-confirmed per the exported artifact's limits.
- The independent teammate handoff sign-off remains open; it requires a human teammate or instructor to run `docs/PERSON1_HANDOFF.md` and sign it (issue #59).
- The selected OCID smoke is complete. Broader OCID coverage and any public
  redistribution of ARID-derived images remain out of scope under D-014.

## Next

- Have an independent teammate run the handoff guide and sign it (issue #59).
- Use the recorded OCID subset for bounded model-execution checks without
  treating replay success as detection accuracy.
- Coordinate with Persons 2-4 on Gate 2-5 detection evidence using the frozen golden pack.

## Evidence

- P1-15 real-model smoke on Windows/Python 3.12.7: four independent OCID source
  sequences completed through `DPT_SwinV2_T_256` on CPU, each yielding finite,
  contiguous 480x640 float32 relative inverse depth. External report:
  `C:\KyraData\model-smoke\midas\midas_ocid_smoke_report.json`, SHA-256
  `06259314dc4c585d2188b23d856b8e81af69604b97ab5e1b6f718246c0c7d27a`;
  checkpoint SHA-256
  `0a859caa18be4bf9375e87dc6b684f6e83dc45b2dc13d8c8b89f6acb2a17a2c5`.
  Latency was not measured, and two-anchor approximate outputs are not accuracy
  evidence.
- P1-15 regression on 2026-09-08: 35 focused MiDaS/baseline/provenance
  tests passed; the full suite passed 250 tests in 175.30s; Ruff,
  byte-compilation, repository consistency, and change-impact validation
  against `origin/main` passed.
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
- P1-15 local Windows/Python 3.12.7 recorded-data verification on 2026-09-08:
  the publisher MD5 and local SHA-256 matched; 8 external manifests and all 168
  frames replayed successfully. This validates source identity, conversion,
  and reader compatibility only; it does not measure detection recall, false
  positives, latency, live-camera behavior, or intent.

# Person 1 Implementation Plan

**Status:** In progress; P1-01/P1-02/P1-03/P1-04..P1-11 are merged, the golden pack is frozen on 2026-09-06 (D-009 confirmed), and P1-12/P1-13 are prepared pending T4 access and independent handoff
**Owner:** Person 1  
**Estimated effort:** 9–14 focused working days, plus access time for the target T4 check  
**Requirements:** [PERSON1_SPEC.md](PERSON1_SPEC.md)

## Outcome

At the end, another teammate can install the core environment, load ten small shelf scenarios, build or reload the opening baseline, inspect data origins, and run all Person 1 checks without Blender, CUDA, network access, or a large dataset.

## Starting point

Present before P1-01:

- Shared contracts in `src/kyra/contracts.py`.
- Strict scenario manifest in `src/kyra/manifest.py`.
- RGB-D replay in `src/kyra/io.py`.
- Baseline building, persistence, and MiDaS alignment in `src/kyra/baseline.py`.

Still not present after P1-03..P1-11 and the frozen golden pack:

- Target-T4 execution evidence (P1-12 T4 leg) and the independent handoff
  sign-off (P1-13).
- Real OCID download and the recorded smoke test on an approved external
  sample.
- `src/kyra/cli.py`, although `pyproject.toml` already names it as a future command.

## Gates before code changes

| Gate | Required decision | Owner | Stop condition |
|---|---|---|---|
| G0.1 | Confirm the current one-package `src/kyra` layout | Person 4 | Complete: approved on 2026-08-26; retain the single `kyra` package and stable `kyra.*` imports. |
| G0.2 | Confirm scenario ten is the second removal shape | Team | Complete: D-009 confirmed on 2026-09-06; the golden pack is frozen. |
| G0.3 | Approve any manifest fields needed for object masks and shape family | Persons 1 and 4 | Do not hide required metadata in free-text notes. |
| G0.4 | Assign the target T4 runner and report location | Person 4 | Proposal recorded 2026-09-06: runner = the team member with T4 access; commands = `docs/PERSON1_HANDOFF.md` steps 1-2; report = `docs/PERSON1_TEST_REPORT_T4_<date>.md`. Local success is not T4 success. |
| G0.5 | Review licences for selected public data, assets, and models | Person 1 plus team | Do not download or redistribute an unapproved source. |

## Work order

The waves are ordered. Tasks within the same wave may be completed together, but a wave closes only when its exit check passes.

### Wave 1 — Freeze contracts and build the test floor

#### P1-01: Write contract tests for existing code

- **Status:** Complete and locally verified on Python 3.12.7 on 2026-08-21.
- **Requirements:** P1-IO-001, P1-IO-002, P1-IO-003, P1-CAL-001, P1-CAL-004, P1-MIDAS-001.
- **Read first:** `contracts.py`, `manifest.py`, `io.py`, `baseline.py`.
- **Create:** `tests/conftest.py`, `tests/test_contracts.py`, `tests/test_manifest.py`, `tests/test_io.py`, `tests/test_baseline.py`.
- **Do:** Build tiny arrays and temporary scenario folders. Test valid values and every named rejection rule. Test baseline save/load and MiDaS good/bad anchors.
- **Proof:** Focused tests pass on Python 3.12 with no optional dependency installed.
- **Current evidence:** The 34 P1-01 tests, plus one P1-02 reader test, pass in
  the pinned Python 3.12.7 environment; Ruff and byte-compilation also pass.
  The tests require no optional GPU, Blender, Open3D, or network dependency.
- **Defects exposed and corrected:** Manifest checksums now cover the exact saved
  bytes; RGB, valid-mask, and occlusion-mask size errors are named clearly; and
  scenario assets cannot escape the scenario folder.
- **Estimate:** 1.5–2 days.

#### P1-02: Resolve contract gaps with Person 4

- **Status:** Complete. The track-annotation reader landed first; the approved
  manifest 1.1 object-mask and shape-family extension was implemented and
  validated on 2026-08-30 as C-006.
- **Requirements:** P1-IO-004, P1-SIM-004.
- **Change proposal:** Add explicit shape-family and object-mask information to the manifest, plus a reader method for track annotations. Keep `FramePacket` unchanged unless Person 4 approves otherwise.
- **Review document:** `docs/P1-02_CONTRACT_CHANGE_PROPOSAL.md` defines the
  exact fields, version rules, compatibility behavior, and approval checklist.
- **Files after approval:** `src/kyra/manifest.py`, `src/kyra/io.py`, matching tests, and this specification.
- **Proof:** Old valid fixtures still load, new required metadata validates, unknown fields still reject, and Person 4 records approval.
- **Current evidence:** `ScenarioFrameSource.track_annotations(frame_id)` returns
  defensive copies, while manifest versions 1.0 and 1.1 load, 1.1 object events
  validate `shape_family` and `object_mask_path`, and
  `ScenarioFrameSource.object_mask(frame_id)` preserves `FramePacket`. The C-006
  record reports 26 focused and 62 full tests passing on 2026-08-30.
- **Estimate:** 0.5–1 day, excluding review wait.

**Wave 1 exit:** Complete. Existing code has passing success and failure tests;
the shared manifest decision and approved C-006 implementation are recorded.

### Wave 2 — Build deterministic scenarios

#### P1-03: Implement the lightweight generator

- **Status:** In review under GitHub issue #14 and pull request #16 on 2026-09-04.
- **Requirements:** P1-SIM-001, P1-SIM-002, P1-SIM-004, P1-SIM-005.
- **Create:** `src/kyra/simulation.py`, `tests/test_simulation.py`.
- **Do:** Generate low-resolution RGB, 16-bit metric depth, valid masks, object masks, occlusion masks, timestamps, calibration, and ground truth from a single seeded random generator. Sort all output and use forward-slash relative paths in manifests.
- **Shape helpers:** Thin box/tray, cylinder, irregular shoe-like union, and handled or hanging object.
- **Proof:** Two runs with the same seed have identical manifest bytes and identical asset SHA-256 maps; a different seed changes the intended randomized fields.
- **Current evidence:** Eight focused offline tests generate and replay removal
  and addition scenarios, cover all four approved shape families, compare
  same-seed bytes and complete file SHA-256 maps, confirm different-seed object
  assets, reject non-empty output folders, and keep manifest paths portable.
- **Estimate:** 2–3 days.

#### P1-04: Create and audit the golden pack

- **Status:** Merged via pull request #27 as `327a905` and frozen on
  2026-09-06 after the D-009 confirmation (frozen status recorded in
  `golden-pack.json`; the canonical-LF audit from WI-025 keeps the inventory
  portable across Windows CRLF and T4 LF checkouts).
- **Current evidence:** Three focused golden-pack tests, plus the eight P1-03
  generator tests, pass offline; they audit ten manifest 1.1 scenarios, all
  four shape families, behavior-specific source evidence, 117 committed files,
  recorded SHA-256 values, and byte-identical regeneration of the frozen pack.
  This is local synthetic evidence and does not close Gate 2 or the target-T4
  check by itself.
- **Requirements:** P1-SIM-003, P1-SIM-005, P1-QA-001.
- **Create:** `scripts/generate_golden_pack.py`, `scenario-fixtures/golden/`, `scenario-fixtures/golden/checksums.sha256`, `tests/test_golden_pack.py`.
- **Do:** Generate the ten scenarios in the specification. Keep fixtures tiny. Freeze seeds, schema version, expected result, and checksums only after G0.2 and G0.3 pass.
- **Proof:** Every manifest validates; every asset exists; all ten expected behaviors and required shape families appear exactly as documented; regeneration is clean.
- **Estimate:** 1–1.5 days.

#### P1-05: Add optional BlenderProc realism checks

- **Requirements:** P1-SIM-006.
- **Create only if approved assets are available:** `scripts/generate_blenderproc_samples.py`, `tests/integration/test_blenderproc_adapter.py`.
- **Do:** Render a small selected sample into the same manifest format. Record BlenderProc version, seed, asset ID, licence, and render settings.
- **Proof:** Core tests still pass when BlenderProc is absent; the optional smoke test passes when installed.
- **Estimate:** 1–2 days. This task is not allowed to block the core golden pack.

**Wave 2 exit:** Complete — the ten-scenario pack is deterministic,
reviewable, small, and independent of heavy tools, and was frozen on
2026-09-06 after the D-009 confirmation.

### Wave 3 — Prove calibration and baseline behavior

#### P1-06: Harden calibration and persistence

- **Status:** Complete; implemented under GitHub issue #21 on 2026-09-06 and
  merged via PR #22 as `ca8715c`. No real gap in `src/kyra/baseline.py` was
  observed; the module landed unchanged.
- **Requirements:** P1-CAL-001, P1-CAL-002, P1-CAL-003, P1-CAL-004.
- **Modify:** `src/kyra/baseline.py`; add focused fixtures in `tests/test_baseline.py`.
- **Do:** Test and correct only observed gaps in 30-frame fusion, noise handling, fixed/portable separation, occupancy bounds, checksum, schema rejection, and save/load equality. Avoid a module move unless G0.1 requires it.
- **Proof:** Fixed shelf pixels never appear in portable components; known sub-0.5 m³ items do; unsafe grids reject; loading does not call `BaselineBuilder.fit`.
- **Estimate:** 1–1.5 days.

#### P1-07: Add known-volume acceptance tests

- **Status:** Complete; implemented under GitHub issue #21 on 2026-09-06 and
  merged via PR #22 as `ca8715c`.
- **Requirements:** P1-CAL-005.
- **Create:** `tests/acceptance/test_baseline_volume.py`.
- **Do:** Use synthetic objects with known volumes at or above 0.5 L, varied position and supported shape families. Compare baseline component volume with ground truth.
- **Proof:** Each accepted case is within 10%; failures print expected volume, measured volume, relative error, and seed.
- **Estimate:** 0.5–1 day.

#### P1-08: Isolate and test MiDaS alignment policy

- **Status:** Complete; implemented under GitHub issue #21 on 2026-09-06 and
  merged via PR #22 as `ca8715c`. Plan deviation recorded: the policy tests
  live in `tests/test_baseline.py` because the issue #18 classifier would
  misclassify the plan-named `tests/test_midas_alignment.py` as Person 4.
- **Requirements:** P1-MIDAS-001, P1-MIDAS-002.
- **Modify only if tests reveal a gap:** `src/kyra/baseline.py`; create `tests/test_midas_alignment.py`.
- **Do:** Cover two or more distinct anchors, empty masks, non-positive metric depth, repeated predictions, large residual, align-before-fit, approximate flag, and metric-evaluation exclusion.
- **Proof:** Bad calibration always rejects; accepted output has finite positive depth only where valid and is labelled approximate.
- **Estimate:** 0.5 day.

**Wave 3 exit:** Complete — the saved baseline is repeatable, and the
assignment’s volume and classification limits pass with the 2026-09-06
evidence under issue #21; handled/hanging overhang cases remain a documented
Person 2 scope limitation.

### Wave 4 — Convert approved public data

#### P1-09: Define and validate provenance

- **Status:** Complete; implemented under GitHub issue #23 on 2026-09-06 and
  merged via PR #24 as `c7de178`.
- **Requirements:** P1-DATA-001, P1-DATA-003.
- **Create:** `data-sources/provenance.json`, `data-sources/README.md`, `tests/test_provenance.py`.
- **Do:** Record source name, official URL, retrieval date, original and computed checksum, licence/terms URL, local external path hint, selected records, exclusions, conversion command, and output schema version. Paths must not expose a developer’s private home folder.
- **Proof:** Schema test rejects missing licence, checksum, selection, or exclusion information.
- **Current evidence:** The committed record covers the OCID source with the
  exact `docs/DATASETS.md` field set, honest `pending_download` status, and
  environment-neutral `<KYRA_DATA_ROOT>/ocid` path hint. The schema test
  rejects missing licence/terms, selection, conversion-command, and checksum
  information, blank exclusion reasons, private home paths, and unknown
  statuses. Plan deviation: delivered as `tests/test_dataset_provenance.py`
  because the change-impact classifier (issue #18) would misclassify the
  plan-named `tests/test_provenance.py` as Person 4.
- **Estimate:** 0.5–1 day.

#### P1-10: Implement the OCID converter

- **Status:** Complete (module, fixture, and tests under issue #23 on
  2026-09-06; CLI entry point published under issue #31 as WI-031).
- **Requirements:** P1-DATA-001, P1-DATA-002.
- **Create:** `src/kyra/ocid.py`, `scripts/convert_ocid.py`, `tests/fixtures/ocid-mini/`, `tests/test_ocid.py`.
- **Do:** Keep filesystem discovery in the script and pure mapping logic in the module. Validate the source checksum first. Preserve frame order, calibration, depth units, and masks. For a valid addition sequence, reverse frame order and update timestamps and expected event to create a removal.
- **Proof:** Mini fixture converts offline; converted manifest loads through `ScenarioFrameSource`; one approved external sample passes a recorded smoke test.
- **Current evidence:** `src/kyra/ocid.py` parses OCID-style TOML strictly,
  maps depth to uint16 millimetres (zero stays unknown), rejects unrepresentable
  depth, extracts valid/object masks, derives windowed addition/removal events
  (first frame is initial state), reverses a valid addition into a removal with
  re-created monotonic timestamps and last-seen object-mask semantics, and
  gates the source by SHA-256. Thirteen tests convert and replay the tiny
  committed fixture through `ScenarioFrameSource`. The local script smoke run
  converted a reversed removal and was replayed; a tampered checksum was
  rejected. The real OCID archive is not downloaded; the recorded smoke test
  on an approved external sample remains pending its retrieval.
- **Estimate:** 1–2 days.

**Wave 4 exit:** Complete for the reproducible-pipeline scope — public data
can be reproduced from a reviewed source without committing bulk data once the
source is downloaded; `scripts/convert_ocid.py` is published (WI-031) and the
real-data smoke test remains pending retrieval.

### Wave 5 — Package, verify, and hand off

#### P1-11: Add a single verification entry point

- **Status:** Implemented under GitHub issue #25 on 2026-09-06; blocked from
  pushing by the issue #18 classifier (every `scripts/*.py` change classifies
  as Person 4/governance).
- **Current evidence:** Seven named checks collect all failures and exit 1 on
  any; absent pack/provenance produces explicit skipped failures instead of a
  vacuous pass. Text assets are hashed with canonical LF so Windows CRLF and
  T4 LF trees verify identically (P1-QA-001 portability), verified green on
  the LF regeneration of the candidate pack, on a CRLF-mangled copy, and later
  against the in-repo pack on the merged `p1/17` tree, with a tamper negative
  control; the script exits 0 only when all checks pass.
- **Requirements:** P1-QA-002.
- **Create:** `scripts/verify_person1.py`.
- **Do:** Run schema, golden checksum, reader, baseline, MiDaS-policy, and provenance checks with clear failure messages. It may call Python functions, but must not download anything.
- **Proof:** One command exits 0 only when every Person 1 acceptance check passes.
- **Estimate:** 0.5 day.

#### P1-12: Validate Windows and target T4

- **Status:** In progress. Windows candidate-leg report drafted on 2026-09-06
  (`docs/PERSON1_TEST_REPORT_WINDOWS_CANDIDATE.md`): 158 tests passed, the
  seven-check verifier exited 0 against the in-repo candidate pack, and the
  change-impact failure was the known issue #18 one (now resolved). The exact
  T4 playbook is prepared in `docs/PERSON1_HANDOFF.md`; the target-T4 leg is
  blocked on G0.4 (runner and report location assigned by Person 4) and on the
  pack freeze decision (D-009), both collected under issue #40.

- **Requirements:** P1-QA-001, P1-QA-002.
- **Use:** Frozen lock files, golden pack, and `docs/PERSON1_TEST_REPORT_TEMPLATE.md`.
- **Do on each environment:** Record OS, CPU/GPU, Python, package versions, Git commit when available, fixture checksum, exact command, exit code, duration, and failures.
- **Proof:** The same golden checksum loads and the full core suite passes in both reports. The local RTX 2050 result is not a substitute for T4 evidence.
- **Estimate:** 0.5 local day plus T4 access time.

#### P1-13: Independent teammate handoff

- **Status:** In progress. The handoff package
  (`docs/PERSON1_HANDOFF.md`) is prepared on 2026-09-06 with exact, recorded
  commands and their real outputs (setup, 161-test suite, seven-check
  verifier, golden regeneration, OCID smoke, baseline/volume, lint and
  consistency gates). The independent-teammate execution and signed report
  remain required; the three blocking decisions are collected under issue #40.
- **Requirements:** P1-QA-003.
- **Do:** Give the reader/generator, golden pack, baseline, converter, MiDaS adapter, provenance, commands, and report template to a teammate who did not implement them.
- **Proof:** The teammate can install, load, run, and explain failures without private instructions; open problems are listed rather than hidden.
- **Estimate:** 0.5 day.

**Wave 5 exit:** Person 1 has a reproducible handoff, not only source files.

## Requirement coverage

| Requirement group | Plan tasks |
|---|---|
| P1-IO | P1-01, P1-02 |
| P1-SIM | P1-02, P1-03, P1-04, P1-05 |
| P1-DATA | P1-09, P1-10 |
| P1-CAL | P1-01, P1-06, P1-07 |
| P1-MIDAS | P1-01, P1-08 |
| P1-QA | P1-04, P1-11, P1-12, P1-13 |

Every specification group maps to at least one implementation task and one stated proof.

## Definition of done

Person 1 is complete only when all of these are true:

- Gates G0.1–G0.5 are recorded.
- Same-seed manifests are byte-identical.
- The ten-scenario checksum is frozen and matches on Windows and T4.
- A saved baseline reloads without recalculation.
- Fixed shelf structure and portable objects pass classification tests.
- Known objects of at least 0.5 L meet the 10% volume limit.
- OCID source, checksum, licence, selection, conversion, and exclusions are documented.
- MiDaS rejection and approximate-depth rules pass.
- All Person 1 tests pass offline.
- An independent teammate signs the handoff report.

## Current implementation checkpoint

P1-01 created the test floor and corrected four input-boundary defects. P1-02
completed the approved manifest 1.1 contract and replay accessors. P1-03 landed
a core generator that uses only locked runtime dependencies and emits synthetic
evidence. P1-04 adds the candidate ten-scenario pack, but that pack remains
unfrozen pending D-009 and does not establish target-T4 or complete Gate 2
evidence. P1-06/P1-07/P1-08 closed Wave 3 with a hardened calibration/noise/
checksum matrix, a within-10% known-volume acceptance suite (with the
hanging-plate bias explicitly recorded as Person 2 scope), and the complete
MiDaS policy matrix. P1-09/P1-10 closed Wave 4's reproducible-pipeline scope:
a validated provenance record and the OCID conversion mapping with a tiny
replayed fixture; the real-data smoke test and the `scripts/convert_ocid.py`
push remain pending issue #18. P1-11 delivers the single verification entry
point locally; it is verified green on LF and CRLF pack trees and on the
merged in-repo pack, and blocked from pushing by issue #18. Remaining Person 1
work: P1-12 environment validation (Windows + target T4), P1-13 independent
teammate handoff, plus D-009/G0.2, the real OCID smoke test, and the
classifier fix to unblock all local-only script pushes.

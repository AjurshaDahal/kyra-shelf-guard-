# Person 1 Implementation Plan

**Status:** In progress; P1-01 is complete and P1-02 is partially implemented  
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

Still not present:

- Deterministic generator and golden pack.
- OCID converter and provenance file.
- Verification scripts and independent test report.
- `src/kyra/cli.py`, although `pyproject.toml` already names it as a future command.

## Gates before code changes

| Gate | Required decision | Owner | Stop condition |
|---|---|---|---|
| G0.1 | Confirm the current one-package `src/kyra` layout | Person 4 | Complete: approved on 2026-08-26; retain the single `kyra` package and stable `kyra.*` imports. |
| G0.2 | Confirm scenario ten is the second removal shape | Team | Do not mark the golden pack frozen until confirmed. |
| G0.3 | Approve any manifest fields needed for object masks and shape family | Persons 1 and 4 | Do not hide required metadata in free-text notes. |
| G0.4 | Assign the target T4 runner and report location | Person 4 | Local success cannot be called T4 success. |
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

- **Status:** Partially implemented on 2026-08-21. The track-annotation reader
  and contract test pass; manifest version 1.1 is documented for review and
  remains approval-gated.
- **Requirements:** P1-IO-004, P1-SIM-004.
- **Change proposal:** Add explicit shape-family and object-mask information to the manifest, plus a reader method for track annotations. Keep `FramePacket` unchanged unless Person 4 approves otherwise.
- **Review document:** `docs/P1-02_CONTRACT_CHANGE_PROPOSAL.md` defines the
  exact fields, version rules, compatibility behavior, and approval checklist.
- **Files after approval:** `src/kyra/manifest.py`, `src/kyra/io.py`, matching tests, and this specification.
- **Proof:** Old valid fixtures still load, new required metadata validates, unknown fields still reject, and Person 4 records approval.
- **Current evidence:** `ScenarioFrameSource.track_annotations(frame_id)` returns
  defensive copies, preserves `FramePacket`, and reports unknown frame IDs. All
  35 tests pass; Ruff and byte-compilation pass. The object-mask and shape-family
  proof remains pending approval and implementation.
- **Estimate:** 0.5–1 day, excluding review wait.

**Wave 1 exit:** Existing code has passing success and failure tests; shared schema
decisions are recorded. The Python 3.12 proof is complete. This remains open only
until the P1-02 contract decision and approved implementation are complete.

### Wave 2 — Build deterministic scenarios

#### P1-03: Implement the lightweight generator

- **Requirements:** P1-SIM-001, P1-SIM-002, P1-SIM-004, P1-SIM-005.
- **Create:** `src/kyra/simulation.py`, `tests/test_simulation.py`.
- **Do:** Generate low-resolution RGB, 16-bit metric depth, valid masks, object masks, occlusion masks, timestamps, calibration, and ground truth from a single seeded random generator. Sort all output and use forward-slash relative paths in manifests.
- **Shape helpers:** Thin box/tray, cylinder, irregular shoe-like union, and handled or hanging object.
- **Proof:** Two runs with the same seed have identical manifest bytes and identical asset SHA-256 maps; a different seed changes the intended randomized fields.
- **Estimate:** 2–3 days.

#### P1-04: Create and audit the golden pack

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

**Wave 2 exit:** The ten-scenario pack is deterministic, reviewable, small, and independent of heavy tools.

### Wave 3 — Prove calibration and baseline behavior

#### P1-06: Harden calibration and persistence

- **Requirements:** P1-CAL-001, P1-CAL-002, P1-CAL-003, P1-CAL-004.
- **Modify:** `src/kyra/baseline.py`; add focused fixtures in `tests/test_baseline.py`.
- **Do:** Test and correct only observed gaps in 30-frame fusion, noise handling, fixed/portable separation, occupancy bounds, checksum, schema rejection, and save/load equality. Avoid a module move unless G0.1 requires it.
- **Proof:** Fixed shelf pixels never appear in portable components; known sub-0.5 m³ items do; unsafe grids reject; loading does not call `BaselineBuilder.fit`.
- **Estimate:** 1–1.5 days.

#### P1-07: Add known-volume acceptance tests

- **Requirements:** P1-CAL-005.
- **Create:** `tests/acceptance/test_baseline_volume.py`.
- **Do:** Use synthetic objects with known volumes at or above 0.5 L, varied position and supported shape families. Compare baseline component volume with ground truth.
- **Proof:** Each accepted case is within 10%; failures print expected volume, measured volume, relative error, and seed.
- **Estimate:** 0.5–1 day.

#### P1-08: Isolate and test MiDaS alignment policy

- **Requirements:** P1-MIDAS-001, P1-MIDAS-002.
- **Modify only if tests reveal a gap:** `src/kyra/baseline.py`; create `tests/test_midas_alignment.py`.
- **Do:** Cover two or more distinct anchors, empty masks, non-positive metric depth, repeated predictions, large residual, align-before-fit, approximate flag, and metric-evaluation exclusion.
- **Proof:** Bad calibration always rejects; accepted output has finite positive depth only where valid and is labelled approximate.
- **Estimate:** 0.5 day.

**Wave 3 exit:** The saved baseline is repeatable and the assignment’s volume and classification limits pass.

### Wave 4 — Convert approved public data

#### P1-09: Define and validate provenance

- **Requirements:** P1-DATA-001, P1-DATA-003.
- **Create:** `data-sources/provenance.json`, `data-sources/README.md`, `tests/test_provenance.py`.
- **Do:** Record source name, official URL, retrieval date, original and computed checksum, licence/terms URL, local external path hint, selected records, exclusions, conversion command, and output schema version. Paths must not expose a developer’s private home folder.
- **Proof:** Schema test rejects missing licence, checksum, selection, or exclusion information.
- **Estimate:** 0.5–1 day.

#### P1-10: Implement the OCID converter

- **Requirements:** P1-DATA-001, P1-DATA-002.
- **Create:** `src/kyra/ocid.py`, `scripts/convert_ocid.py`, `tests/fixtures/ocid-mini/`, `tests/test_ocid.py`.
- **Do:** Keep filesystem discovery in the script and pure mapping logic in the module. Validate the source checksum first. Preserve frame order, calibration, depth units, and masks. For a valid addition sequence, reverse frame order and update timestamps and expected event to create a removal.
- **Proof:** Mini fixture converts offline; converted manifest loads through `ScenarioFrameSource`; one approved external sample passes a recorded smoke test.
- **Estimate:** 1–2 days.

**Wave 4 exit:** Public data can be reproduced from a reviewed source without committing bulk data.

### Wave 5 — Package, verify, and hand off

#### P1-11: Add a single verification entry point

- **Requirements:** P1-QA-002.
- **Create:** `scripts/verify_person1.py`.
- **Do:** Run schema, golden checksum, reader, baseline, MiDaS-policy, and provenance checks with clear failure messages. It may call Python functions, but must not download anything.
- **Proof:** One command exits 0 only when every Person 1 acceptance check passes.
- **Estimate:** 0.5 day.

#### P1-12: Validate Windows and target T4

- **Requirements:** P1-QA-001, P1-QA-002.
- **Use:** Frozen lock files, golden pack, and `docs/PERSON1_TEST_REPORT_TEMPLATE.md`.
- **Do on each environment:** Record OS, CPU/GPU, Python, package versions, Git commit when available, fixture checksum, exact command, exit code, duration, and failures.
- **Proof:** The same golden checksum loads and the full core suite passes in both reports. The local RTX 2050 result is not a substitute for T4 evidence.
- **Estimate:** 0.5 local day plus T4 access time.

#### P1-13: Independent teammate handoff

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

## First implementation session

P1-01 created the test floor and exposed four input-boundary defects, which are now
fixed. P1-02 is now split into a completed track-annotation reader change and an
approval-gated manifest version 1.1 proposal. The pinned Python 3.12.7 environment
is installed and all 35 current tests pass there.

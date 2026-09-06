# Person 1 Handoff Package

**Purpose:** an independent teammate (someone who did not implement Person 1)
can follow this guide to install the environment, replay and verify every
Person 1 deliverable, and reproduce the stated results without private
instructions.

**Prepared:** 2026-09-06 by the Person 1 implementation agent.
**Commit:** `1445f47` + branch `p1/39-handoff-and-decisions` changes.
**Recorded environment:** Microsoft Windows 11 (10.0.26200), Intel Core
i5-12450H, NVIDIA RTX 2050 (unused for core checks), Python 3.12.7,
`requirements.lock` SHA-256 `8BB50C875D989B2F5C930C684E17C602282D2415973CE7EF0CB6B27F2FED5FBF`.

## What Person 1 produced

| Deliverable | Location | Notes |
|---|---|---|
| Deterministic scenario generator | `src/kyra/simulation.py` | Offline, seeded, four shape families |
| Candidate golden pack (ten scenarios) | `scenario-fixtures/golden/` | 117 files, 62,614 canonical-LF bytes; **candidate, not frozen** (D-009) |
| Baseline builder and persistence | `src/kyra/baseline.py` | 30-frame fusion, save/load, MiDaS policy |
| Known-volume acceptance suite | `tests/acceptance/test_baseline_volume.py` | ≤10% error for ≥0.5 L cases |
| OCID conversion | `src/kyra/ocid.py`, `scripts/convert_ocid.py` | Addition-to-removal reversal included |
| Provenance record | `data-sources/provenance.json` | OCID pending download (P-003) |
| Reader replay | `src/kyra/io.py` | Depth uint16 mm → float32 m; zero stays unknown |
| Verification entry point | `scripts/verify_person1.py` | Seven checks, exit 0 only when all pass |

## Setup (reproducible, offline after install)

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.lock
.\.venv\Scripts\python.exe -m pip install -e .
```

No GPU, Blender, model download, or network access is needed for the checks.

## Playbook — every command actually run on 2026-09-06

### 1. Full automated suite

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

Recorded result: `161 passed in 4.60s` (Python 3.12.7, current pins numpy
2.4.6 / OpenCV 5.0.0 / pydantic 2.13.4). This includes the golden-pack
regeneration audit (byte-identical) and the volume acceptance suite.

### 2. Single verification entry point

```powershell
.\.venv\Scripts\python.exe scripts\verify_person1.py --golden scenario-fixtures\golden --provenance data-sources\provenance.json
```

Recorded result: seven `[OK]` lines
(golden pack present, manifest schema, golden checksums, reader replay,
baseline build, MiDaS policy, provenance record) and exit code 0. A tampered
asset makes the affected checks fail with explicit messages (verified
2026-09-06 with an edited PNG and JSON).

### 3. Golden-pack regeneration

```powershell
.\.venv\Scripts\python.exe scripts\generate_golden_pack.py <empty-output-directory>
```

Recorded result: `Generated candidate golden pack: <dir>`; the regenerated
`checksums.sha256` is byte-identical to `scenario-fixtures/golden/checksums.sha256`.
`golden-pack.json` records `pack_status: candidate` (10 scenarios, behavior
matrix, all four shape families).

### 4. OCID conversion smoke (mini fixture)

```powershell
.\.venv\Scripts\python.exe scripts\convert_ocid.py tests\fixtures\ocid-mini\ocid\sequence-01 <out> --shelf <shelf.json> --expected-sha256 15EB0FEEC6673036AD530A1AE55A5F241A491C07F446ACB68D8AEB9801F9D801 --scenario-id smoke --seed 1 --reverse
```

Recorded result: exit 0, three frames, manifest SHA-256
`19c5e7ccaefa94e5e310fc94146533ddb9268dba552928f32389a85ff358ff15`; the
reversed removal replays through `ScenarioFrameSource` with the last-seen
object mask on the removal frame. A wrong `--expected-sha256` is rejected with
exit 2.

### 5. Baseline round trip and volume

Covered by the automated suite: `tests/test_baseline.py` (save/load equality,
no recomputation on load, checksum stability) and
`tests/acceptance/test_baseline_volume.py` (box, cylinder, irregular L cases
0.55-1.72 L within 10%; a hanging-plate guard case documents the known
void-column overestimate as Person 2 scope).

### 6. Lint and repository consistency

```powershell
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m compileall -q src tests scripts
.\.venv\Scripts\python.exe scripts\check_repo_consistency.py
.\.venv\Scripts\python.exe scripts\check_change_impact.py --base origin/main
```

Recorded result: all pass (2026-09-06).

## Expected results summary

| Check | Expected | Recorded |
|---|---|---|
| `pytest -q` | 161 passed | 161 passed |
| `verify_person1.py` | 7 OK, exit 0 | 7 OK, exit 0 |
| golden regeneration | byte-identical inventory | byte-identical |
| OCID convert (correct checksum) | exit 0 + replay | exit 0, manifest `19c5e7cc…` |
| OCID convert (wrong checksum) | exit 2 | exit 2 |
| ruff / compileall / consistency / change-impact | pass | pass |

## What is not claimed

- The golden pack is **not frozen**: it needs the D-009 team confirmation, and
  its checksums must not be treated as frozen evidence.
- Target-T4 performance and portability are **not proven**: only the Windows
  laptop leg exists (`docs/PERSON1_TEST_REPORT_WINDOWS_CANDIDATE.md`).
- The real OCID archive has **not been downloaded** or converted: the
  provenance record is honest `pending_download`, and P-003 licence review is
  required first.
- There is **no end-to-end** camera-to-alert system; Gates 3-7 and Person 2/3
  downstream integration remain open.

## Decision packets (one approval each, tracked under issue #40)

1. **D-009 — confirm the tenth golden scenario.** The pack uses the
   D-009-provisional irregular-item removal as G03 + scenario ten = second
   removal shape family. Confirming D-009 permits the pack's checksums to be
   frozen and the P1-12 T4 leg to run with them. Ask: does the team accept the
   second-removal interpretation as scenario ten?
2. **P-003 — licence review for public data.** The sole planned source, OCID
   (official page:
   https://www.acin.tuwien.ac.at/en/vision-for-robotics/software-tools/object-clutter-indoor-dataset/),
   must be confirmed as permitting research use, derivative conversion, tiny
   fixture redistribution, and publication of examples before download.
3. **G0.4 — assign the target-T4 runner and report location.** The Windows
   leg is recorded; the T4 leg needs a runner (Person 4/team assignment) and a
   stored report path. The exact T4 commands are these steps 1 and 2 re-run in
   that environment.

## Sign-off (independent teammate, P1-QA-003)

| Item | Value |
|---|---|
| Tester (not the implementer): | |
| Date: | |
| Commands run and results: | |
| Problems found / open items: | |
| Signature: | |
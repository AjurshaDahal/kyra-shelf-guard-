# Testing and Evidence Guide

## Current truth

The current suite contains 39 tests: 35 product-foundation tests across contracts,
manifests, RGB-D input, track-annotation access, baseline persistence, and MiDaS
anchor alignment, plus four repository-governance tests. On 2026-08-24 all 39
passed in the pinned Python 3.12.7 environment; Ruff, byte-compilation,
repository consistency, and change-impact validation also passed.

## Test layers

| Layer | Purpose | Planned location | External needs |
|---|---|---|---|
| Unit | Check one conversion, validator, calculation, or rejection | `tests/test_*.py` | None |
| Contract | Prove saved files and public values match the shared schema | `tests/test_manifest.py`, `tests/test_io.py` | None |
| Determinism | Compare repeated generated output | `tests/test_simulation.py` | None |
| Golden pack | Load the candidate or frozen scenarios and audit expected metadata | `tests/test_golden_pack.py` | Tiny committed fixtures |
| Acceptance | Check volume error and baseline behavior | `tests/acceptance/` | Tiny synthetic fixtures |
| Conversion | Check OCID mapping | `tests/test_ocid.py` | Tiny mini fixture; real smoke test is separate |
| Optional integration | Check BlenderProc or full public data path | `tests/integration/` | Explicit optional environment |
| Cross-platform | Repeat the core suite on Windows and target T4 | Test reports | Two environments |

## Golden scenario matrix

| ID | Behavior | Expected suspicious alert | Main assertion |
|---|---|---:|---|
| G01 | No change | No | Stable baseline and event frames |
| G02 | Thin-item removal | Yes | Correct removal time, mask, and volume |
| G03 | Irregular-item removal | Yes | Second shape family; provisional team choice |
| G04 | Addition | No removal alert | Change direction is addition |
| G05 | Person-only occlusion | No | Occluded pixels are not counted as removal |
| G06 | Removal then occlusion | Yes when visible evidence is sufficient | Removal evidence survives later occlusion |
| G07 | Authorized restocking | No suspicious alert | Authorized/restock state is preserved |
| G08 | Lighting variation | No | RGB-only change does not alter metric depth result |
| G09 | Invalid depth | No alert from missing values | Unknown is not free space |
| G10 | Camera drift | Reject or suppress | Drift beyond threshold is not trusted |

The pack must also cover envelopes or trays, cylinders, irregular shoes, and handled or hanging objects. One scenario may satisfy more than one shape-coverage need.

## Mandatory assertions

### Reader and manifest

- Millimetres become metres exactly within floating-point tolerance.
- RGB is `uint8`; depth is two-dimensional `float32`; masks are boolean.
- Invalid depth remains invalid.
- Missing files, wrong data type, size mismatch, duplicate IDs, bad order, and bad baseline references fail clearly.
- Occlusion and track annotations remain available.

### Determinism

- Same settings and seed produce byte-identical manifest files.
- Asset SHA-256 maps also match.
- Output does not contain machine-specific absolute paths.
- Different seeds change only intended randomized content.

### Baseline

- 29 frames reject and 30 clear frames succeed.
- Median depth and noise estimate handle missing samples.
- Fixed shelf structure is never a portable component.
- Eligible objects under 0.5 m³ are portable.
- The default occupancy cell is 1 cm.
- Save/load preserves arrays, metadata, schema, and checksum.
- Loading does not rerun calibration.
- Synthetic objects of at least 0.5 L have at most 10% volume error.

### MiDaS policy

- Fewer than two anchors reject.
- Empty, non-positive, repeated, or inconsistent anchors reject.
- Align-before-fit rejects.
- Accepted aligned output is marked approximate.
- Approximate output is excluded from the primary metric-volume score unless calibration succeeds.

### Provenance and conversion

- Required source, licence, checksum, selection, exclusion, and conversion fields are present.
- OCID mini fixture converts and reloads offline.
- Reversed sequences keep increasing timestamps and correct removal truth.
- Bulk external data never appears in the repository.

## Commands

Normal project checks:

```powershell
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\python.exe -m pytest --cov=kyra --cov-report=term-missing
.\.venv\Scripts\python.exe -m ruff check .
```

Regenerate the candidate golden pack only into a new or empty directory, then
run its focused audit with the generator tests:

```powershell
.\.venv\Scripts\python.exe scripts\generate_golden_pack.py <empty-output-directory>
.\.venv\Scripts\python.exe -m pytest tests\test_simulation.py tests\test_golden_pack.py -q
```

The committed pack is intentionally marked `candidate`. Successful local
regeneration does not make it frozen, close D-009, prove target-T4 portability,
or establish downstream alert behavior.

Once P1-11 creates the verification script:

```powershell
.\.venv\Scripts\python.exe scripts\verify_person1.py
```

Do not use coverage percentage as a substitute for the explicit acceptance limits.

## Latest foundation evidence

Local commands completed successfully on Python 3.12.7 on 2026-08-24:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m compileall -q src tests
```

Result: 39 tests passed; lint and byte-compilation passed. This closes the local
Python 3.12 foundation proof, but it does not replace later golden-pack, target
T4, or independent handoff evidence.

For dependency-security changes, reinstall `requirements.lock`, reinstall the
editable package, run the complete local checks, and require both Python CI jobs.
An optional Torch pin may be verified as published and advisory-fixed without
being treated as an installed GPU or target-T4 acceptance result.

## Repository governance checks

Run these before every pull request:

```powershell
.\.venv\Scripts\python.exe scripts\check_repo_consistency.py
.\.venv\Scripts\python.exe scripts\check_change_impact.py --base origin/main
```

The first command checks required control documents, status structure, and
relative Markdown links. The second checks the changed-file set: code requires
an owner-status update, work-item record, and changelog; contracts and
dependencies require their additional synchronized documentation. These checks
validate repository consistency, not algorithm correctness.

## Owner proof summary

| Owner | Minimum independent proof before integration |
|---|---|
| Person 1 | Malformed/valid replay; deterministic bytes; 30-frame baseline; persistence/checksum; MiDaS anchor failures; converter provenance; ten-pack loading |
| Person 2 | Registration tolerance; signed addition/removal; unknown-depth and occlusion suppression; cluster persistence; known-volume error |
| Person 3 | Replay-track determinism; lazy optional model loading; mask alignment; proximity window; authorization suppression; deterministic alert rule |
| Person 4 | Contract/mocks compatibility; bounded pipeline behavior; five CLI commands; frozen evaluation split; comparison report; clean-environment run |

Exact gate evidence and owners are listed in `docs/INTEGRATION_GATES.md`.

## Windows and T4 evidence

Run the same frozen golden pack and core dependency lock in both environments. Complete [PERSON1_TEST_REPORT_TEMPLATE.md](PERSON1_TEST_REPORT_TEMPLATE.md) for each run. Record failures honestly; a Windows RTX 2050 run cannot prove target T4 compatibility.

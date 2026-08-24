# Kyra Shelf Guard

Kyra is a university project that detects suspicious shelf removals from recorded RGB and depth images. It measures physical change on a shelf; it does not need a separate trained model for every product.

This repository is at an early foundation stage. The shared data contracts,
scenario manifest, RGB-D reader, baseline builder, baseline save/load, MiDaS
alignment helper, and first foundation tests exist. The deterministic scenario
generator, golden scenario pack, OCID converter, and command-line entry point
still need to be built.

## Person 1 in simple words

Person 1 prepares trustworthy input for the rest of the team:

1. Create or convert recorded shelf scenes.
2. Make the same test scene repeat exactly when given the same seed.
3. Build the opening picture of what the shelf normally looks like.
4. Save that opening picture so the team can reuse it.
5. Record where every dataset came from and what its licence allows.
6. Hand the input and baseline to Persons 2, 3, and 4.

Person 1 does **not** build person tracking, final removal detection, alert rules, or the final reporting pipeline.

## Current state

| Area | Status | Evidence |
|---|---|---|
| Shared Python data objects | Present | `src/kyra/contracts.py` |
| Scenario manifest and checksum | Present | `src/kyra/manifest.py` |
| RGB-D scenario reader | Present, foundation tests pass | `src/kyra/io.py`, `tests/test_io.py` |
| Baseline build and save/load | Present, foundation tests pass | `src/kyra/baseline.py`, `tests/test_baseline.py` |
| MiDaS anchor alignment | Present, foundation tests pass | `src/kyra/baseline.py`, `tests/test_baseline.py` |
| Deterministic scenario generator | Not built | Planned in the Person 1 plan |
| Ten-scenario golden pack | Not built | Planned in the Person 1 plan |
| OCID converter and provenance file | Not built | Planned in the Person 1 plan |
| Test suite | P1-01 foundation plus P1-02 reader test: 35 tests | Passed on Python 3.12.7 |
| `kyra` command | Not built | `pyproject.toml` points to a future `kyra.cli` module |

The foundation checks pass in the pinned Python 3.12.7 environment. Later
assignment acceptance tests for the generator, golden pack, volume limits,
public-data conversion, and target T4 are still planned.

## Can this laptop complete Person 1?

Yes. The current ASUS Vivobook has a Core i5-12450H, about 16 GB RAM, an RTX 2050 with 4 GB graphics memory, and Python 3.12. That is enough for the scenario reader, lightweight procedural scenarios, calibration, baseline work, OCID conversion, and tests.

Use the laptop for the complete CPU-first Person 1 path. Keep large datasets outside Git, render small batches in BlenderProc, and use the target T4 environment only for the final compatibility check. See [System Requirements](docs/SYSTEM_REQUIREMENTS.md) for the exact storage and workload guidance.

## Quick setup on Windows

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.lock
.\.venv\Scripts\python.exe -m pip install -e .
```

The normal checks are:

```powershell
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\python.exe -m ruff check .
```

Do not run `kyra` yet; its command module is still planned work.

## Documentation

- [Person 1 Specification](docs/PERSON1_SPEC.md) — the exact responsibilities and acceptance rules.
- [Person 1 Implementation Plan](docs/PERSON1_IMPLEMENTATION_PLAN.md) — the work order, files, dependencies, and proof required for every stage.
- [System Requirements](docs/SYSTEM_REQUIREMENTS.md) — what can run locally and what needs the target T4 check.
- [Architecture](docs/ARCHITECTURE.md) — how Person 1 connects to the rest of the system.
- [Development Guide](docs/DEVELOPMENT.md) — setup and dependency groups.
- [Testing Guide](docs/TESTING.md) — unit, contract, golden-pack, and cross-platform checks.
- [Dataset and Provenance Rules](docs/DATASETS.md) — external data, checksums, licences, and exclusions.
- [Decisions](docs/DECISIONS.md) — important choices that must stay consistent.
- [Project Skills](SKILLS.md) — the practical skills and evidence Person 1 must deliver.
- [Contributing](CONTRIBUTING.md) — change workflow and review rules.
- [Changelog](CHANGELOG.md) — notable repository changes.
- [AI navigation index](llms.txt) and [agent instructions](AGENTS.md).

## Assignment source

The controlling assignment is [Four-Person Physics-Based Shelf Removal Detection Plan](Four-Person_Physics-Based_Shelf_Removal_Detection_Plan.docx). If a repository document conflicts with that assignment, the assignment wins and the repository document must be corrected.

## Licence

The code is declared as `AGPL-3.0-only`; the full text is in [LICENSE](LICENSE). Before public distribution, the team must still confirm that every selected dataset, 3D asset, and optional model licence is compatible with the intended use. Dataset and model licences remain separate from the code licence.

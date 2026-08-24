# AGENTS.md

This file gives coding agents the project rules that are too detailed for the human-facing README. Read it before changing this repository.

## Read first

1. `README.md`
2. `docs/PERSON1_SPEC.md` when working on Person 1 scope
3. `docs/PERSON1_IMPLEMENTATION_PLAN.md` for task order and acceptance checks
4. `docs/DECISIONS.md` for locked choices
5. `docs/DATASETS.md` before downloading, generating, or converting data
6. `docs/TESTING.md` before claiming completion
7. The controlling assignment DOCX when requirements are unclear

## Project boundary

Kyra detects shelf change from replayable RGB-D input. It may use pretrained person tracking and an optional MiDaS fallback, but the central geometry path must not require SKU-specific or theft-scenario training.

Person 1 owns input data, deterministic simulation, calibration, baseline generation, dataset conversion, and data provenance. Person 1 does not own geometry differencing, person tracking, alert rules, orchestration, or final evaluation.

Shared contracts are team-owned. Do not change a public contract just to make a Person 1 implementation easier. Record the requested change and obtain approval from Person 4 and every affected owner.

## Current source layout

- `src/kyra/contracts.py`: shared arrays, enums, and event objects.
- `src/kyra/manifest.py`: strict scenario JSON models and manifest checksums.
- `src/kyra/io.py`: replayable RGB-D reader.
- `src/kyra/baseline.py`: baseline build, save/load, and MiDaS anchor alignment.
- `tests/`: P1-01 foundation tests for contracts, manifests, RGB-D input,
  baseline persistence, and MiDaS alignment.
- `scenario-fixtures/`: planned; only tiny committed golden fixtures belong here.
- `scripts/`: planned; dataset conversion and verification entry points belong here.

The `kyra` console entry in `pyproject.toml` is not usable until `src/kyra/cli.py` exists.

## Non-negotiable implementation rules

- Use Python 3.12 on this Windows laptop. Keep `requires-python >=3.11` compatibility unless the team changes it deliberately.
- Store depth as 16-bit PNG millimetres on disk and `float32` metres in memory.
- Treat zero, NaN, and masked depth as unknown, never as empty shelf space.
- Keep timestamps in integer nanoseconds and require monotonic frame order.
- Make deterministic generation independent of network access, CUDA, Blender, and downloaded assets.
- Derive every random choice from the scenario seed. Sort file lists and JSON keys where byte stability matters.
- Keep large datasets, generated batches, weights, point clouds, and run output outside Git.
- Commit only tiny, reviewed golden fixtures needed for deterministic tests.
- Record source URL, dataset version, checksum, licence, selected records, conversion command, and exclusions for external data.
- Never report synthetic or tracker-only evidence as real end-to-end evidence.
- Do not invent benchmark results. A check passes only when its command has actually completed successfully.
- Make the smallest change that satisfies a traced requirement. Avoid unrelated refactors.

## Setup and checks

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.lock
.\.venv\Scripts\python.exe -m pip install -e .
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\python.exe -m ruff check .
```

Install optional groups only for the task that needs them:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-simulation.lock
.\.venv\Scripts\python.exe -m pip install -r requirements-gpu.lock
```

Core Person 1 tests must pass with `requirements.lock` alone. BlenderProc, Open3D, Torch, MiDaS model downloads, CUDA, and network access are integration or extended-data dependencies, not unit-test requirements.

## Required proof for Person 1 changes

- Reader change: malformed-file tests and a valid replay test.
- Manifest change: schema validation, canonical serialization, and same-seed checksum test.
- Generator change: same seed produces byte-identical manifests and stable assets.
- Baseline change: 30-frame calibration test, fixed/portable classification tests, checksum test, and reload-without-recompute test.
- MiDaS change: good anchors pass, missing/inconsistent anchors fail, and successful results are marked approximate.
- Dataset converter change: fixture conversion test plus provenance/checksum output; no live download in unit tests.
- Golden-pack change: all ten scenarios load on Windows and in the target T4 environment.

## Documentation maintenance

- Update `CHANGELOG.md` under `Unreleased` for notable changes.
- Update `docs/PERSON1_SPEC.md` only when the assignment or an approved team decision changes scope.
- Update `docs/PERSON1_IMPLEMENTATION_PLAN.md` task status and evidence links as work lands.
- Update `docs/DECISIONS.md` when a durable design choice changes.
- Update `llms.txt` when a new authoritative document is added.

## Git and review safety

This folder was not a Git repository when these documents were prepared. Do not invent commit history or claim that changes were pushed. After the team initializes or connects Git, use small commits, name the requirement IDs in the commit or pull-request description, and never commit external datasets or generated bulk output.

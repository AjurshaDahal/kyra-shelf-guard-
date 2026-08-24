# Development Guide

## Supported local path

Use Python 3.12 on this Windows laptop. The package declares Python 3.11 or newer, but Python 3.13 is also installed and may be less compatible with optional scientific packages.

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.lock
.\.venv\Scripts\python.exe -m pip install -e .
```

The core lock includes development checks. No GPU, Blender, model download, or network access should be needed after installation.

## Optional environments

Install only one heavy path when a task requires it:

```powershell
# BlenderProc scenario work
.\.venv\Scripts\python.exe -m pip install -r requirements-simulation.lock

# Open3D, Torch, tracking, or full MiDaS experiments
.\.venv\Scripts\python.exe -m pip install -r requirements-gpu.lock
```

Do not add heavy packages to `requirements.lock`. Core replay and tests must stay lightweight.

## Repository layout

```text
src/kyra/                 Python package
tests/                    Planned unit, contract, integration, and acceptance tests
scripts/                  Planned generation, conversion, and verification entry points
scenario-fixtures/golden/ Planned tiny frozen scenarios
data-sources/             Planned provenance records, not bulk data
docs/                     Specifications and operating guides
```

Large datasets and render caches belong outside `D:\Code\Kyra`. See [DATASETS.md](DATASETS.md).

## Normal checks

After the test files exist:

```powershell
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\python.exe -m ruff check .
```

Useful focused checks after implementation:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_io.py
.\.venv\Scripts\python.exe -m pytest tests\test_baseline.py
.\.venv\Scripts\python.exe scripts\verify_person1.py
```

The last three commands describe planned files and will fail until their implementation tasks are complete.

## Current command warning

`pyproject.toml` declares a `kyra` command, but `src/kyra/cli.py` does not exist. Do not use or document the command as working yet. Person 4 should coordinate the final shared CLI.

## Change rules

- Name the relevant `P1-*` requirement in the test or change description.
- Add a failure test before correcting behavior.
- Keep units in variable names where practical: `_m`, `_m3`, `_mm`, `_ns`.
- Use deterministic ordering and one explicit random seed.
- Keep network and bulk data out of tests.
- Do not change shared contracts or schema meaning without recording approval.
- Update `CHANGELOG.md` for notable changes and `docs/DECISIONS.md` for durable choices.

## Evidence to retain

For each acceptance run, retain the exact command, environment, dependency versions, exit code, fixture checksum, and result. A source file, installed package, or successful import alone is not acceptance proof.

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

## Dependency security updates

Treat a dependency pin as a synchronized change: update `pyproject.toml` and every affected `requirements*.lock`, record the advisory and owner impact in a work item, update testing/status documentation, and rerun the applicable clean install. Core build/test dependencies must pass Python 3.11 and 3.12 CI. Optional GPU dependency changes additionally require a target-T4 smoke run before Gate 7; updating a pin or resolving a repository alert is not T4 compatibility evidence.

## Repository layout

```text
src/kyra/                 Python package
tests/                    Planned unit, contract, integration, and acceptance tests
scripts/                  Governance checks plus planned generation/conversion tools
scenario-fixtures/golden/ Planned tiny frozen scenarios
data-sources/             Planned provenance records, not bulk data
docs/                     Authority, status, work items, specifications, and evidence
.github/                  Issue/PR templates, ownership, CI, and dependency updates
```

Large datasets and render caches belong outside `D:\Code\Kyra`. See [DATASETS.md](DATASETS.md).

## Normal checks

Normal code and governance checks:

```powershell
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m compileall -q src tests scripts
.\.venv\Scripts\python.exe scripts\check_repo_consistency.py
```

Useful focused checks after implementation:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_io.py
.\.venv\Scripts\python.exe -m pytest tests\test_baseline.py
.\.venv\Scripts\python.exe scripts\verify_person1.py
```

`verify_person1.py` remains planned and will fail until its implementation task
is complete. The focused pytest commands work today.

## Git workflow

Fetch `origin`, branch from current `main`, and name the branch
`<owner>/<issue>-<slug>`. Run `AGENTS.md` preflight before editing. Before a
pull request, compare the branch with `origin/main`:

```powershell
git fetch origin
.\.venv\Scripts\python.exe scripts\check_change_impact.py --base origin/main
```

Code and governance changes must carry the status, work-item, changelog, and
documentation companions defined in [DOCUMENTATION_POLICY.md](DOCUMENTATION_POLICY.md).
The authoritative command sequence for creating or synchronizing a branch,
reviewing and staging a diff, committing, and pushing is in
[COLLABORATION_WORKFLOW.md](COLLABORATION_WORKFLOW.md). This development guide
does not define a separate Git policy.

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

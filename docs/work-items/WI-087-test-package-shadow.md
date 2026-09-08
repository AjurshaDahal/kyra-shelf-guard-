# WI-087 — Prevent optional dependency test-package shadowing

- **Owner:** P4
- **Status:** In review
- **Started:** 2026-09-08
- **Completed:** 2026-09-08
- **Requirements:** test infrastructure compatibility
- **Integration gate:** None

## Objective

Keep repository test-helper imports deterministic after installing the pinned
optional model dependencies.

## In scope

- Add the standard package marker to the repository `tests` directory.
- Re-run the previously failing Gate 3 imports and the full suite.

## Out of scope

- Runtime pipeline, model adapters, detection logic, or public contracts.

## Inputs, outputs, and contracts

The optional dependency environment contains a top-level site-packages
`tests` package. Python must resolve `tests.*` helper imports to this repository.
There is no production data-contract change.

## Implementation summary

Added `tests/__init__.py` so the repository test directory wins deterministic
package resolution from the project root.

## Documentation impact

The changelog and Person 4 status record the environment-specific cause and
the deliberately test-only fix.

## Verification

| Environment | Command | Result | Evidence |
|---|---|---|---|
| Windows 11, Python 3.12.7, pinned optional model dependencies | `python -c "import tests; print(tests.__file__)"` | Passed | Resolved to repository `tests/__init__.py` |
| Same | `python -m pytest tests/test_geometry_gate3.py -q` | Passed: 5 tests | GitHub issue #87 |
| Same | `python -m pytest -q` | Passed: 246 tests | GitHub issue #87 |
| Same | Ruff, byte-compile, consistency, change impact | Passed | GitHub issue #87 |

## Risks, limitations, and failures

This only fixes test import resolution. It provides no evidence about model
quality, detection accuracy, live cameras, or latency.

## Handoff

Person 4 reviews and merges the test-infrastructure-only patch before model
execution evidence is treated as a clean repository verification.

## Final links

- Issue: https://github.com/DontHash/kyra-shelf-guard/issues/87
- Pull request: Pending
- Commit: Pending

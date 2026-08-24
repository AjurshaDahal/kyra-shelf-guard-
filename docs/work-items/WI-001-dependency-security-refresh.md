# WI-001 — Dependency Security Refresh

- **Owner:** Person 4 / repository steward
- **Status:** In progress
- **Started:** 2026-08-24
- **Integration gate:** Repository foundation; target-T4 proof remains Gate 7

## Objective

Resolve the six dependency alerts GitHub reported after the first private-repository push without misrepresenting an optional-package pin update as GPU or target-T4 acceptance.

## In scope

- Update Wheel for GHSA-8rrh-rw8j-w5fx.
- Update pytest for GHSA-6w46-j5rx-g56g.
- Update Setuptools for GHSA-h35f-9h28-mq5c.
- Update optional Torch for GHSA-vgrw-7cvw-pwgx, GHSA-qfhq-4f3w-5fph, and GHSA-rrmf-rvhw-rf47.
- Synchronize `pyproject.toml`, core/GPU lock files, development/testing guidance, changelog, and status.
- Reinstall and verify the lightweight core environment locally and in hosted Python 3.11/3.12 CI.

## Out of scope

- Installing the large optional Torch/GPU environment merely to close a metadata alert.
- Claiming CUDA, model, performance, or target-T4 compatibility.
- Changing a runtime contract or tracking algorithm.

## Contract impact

No shared runtime contract change.

## Verification

Local verification completed on Windows with Python 3.12.7:

- core lock and editable package reinstalled successfully;
- installed versions: pytest 9.0.3, Setuptools 83.0.0, Wheel 0.46.2;
- `python -m pip check`: no broken requirements;
- `python -m pytest`: 39 passed;
- Ruff, compileall, and repository consistency checks passed.

Pending: change-impact validation on the staged change, hosted Python 3.11/3.12 CI, and the GitHub dependency-alert rescan.

PyPI index and GitHub advisory metadata confirmed that each selected exact version exists and meets the first patched version. Optional Torch 2.13.0 is not installed or target-T4 validated by this work item.

## Limitations and next action

Person 3 and Person 4 must run the optional tracking/MiDaS environment on the target T4 before Gate 7. A zero-alert repository scan does not replace that evidence.

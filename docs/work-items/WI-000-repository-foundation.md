# WI-000 — Repository Collaboration Foundation

- **Owner:** Person 4 / repository steward
- **Status:** In progress
- **Started:** 2026-08-24
- **Integration gate:** Gate 1 foundation

## Objective

Create the private GitHub repository and establish durable, machine-checked collaboration controls before the four workstreams expand implementation.

## In scope

- Recoverable Git baseline.
- Project charter, owner boundaries, contract registry/change process, status and integration-gate records.
- Human/agent issue-to-merge and handoff workflow.
- GitHub templates, CODEOWNERS, dependency updates, CI, and repository/change-impact validation.
- Private GitHub remote creation, push, and verification.

## Out of scope

- Product algorithm changes.
- Approving P-001 or P-005.
- Inventing team GitHub handles.
- Claiming branch protection that the GitHub account/plan does not enforce.

## Contract impact

No runtime contract changes. Existing shared types and manifest semantics remain unchanged.

## Documentation impact

Repository-wide collaboration documentation, status, decisions, changelog, README, contributor/agent guidance, and AI navigation index.

## Verification

Local foundation verification completed on 2026-08-24 with Python 3.12.7:

- `python -m pytest`: 39 passed.
- `python -m ruff check .`: passed.
- `python -m compileall -q src tests scripts`: passed.
- `python scripts/check_repo_consistency.py`: passed.
- `python scripts/check_change_impact.py --base HEAD`: passed for 43 changed files.
- `git diff --cached --check`: passed.

Local/remote SHA, GitHub visibility/default branch, and hosted workflow results remain pending until the private remote is created.

## Limitations and next action

Team reviewer handles remain unassigned. After remote creation, add Persons 1–4 to the roster/CODEOWNERS and configure required reviews/checks using those real handles.

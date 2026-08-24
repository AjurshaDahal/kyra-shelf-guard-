# WI-000 — Repository Collaboration Foundation

- **Owner:** Person 4 / repository steward
- **Status:** Complete
- **Started:** 2026-08-24
- **Completed:** 2026-08-24
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

Hosted verification completed on 2026-08-24:

- Repository: [DontHash/kyra-shelf-guard](https://github.com/DontHash/kyra-shelf-guard).
- Visibility: `PRIVATE`; default branch: `main`.
- Local and `origin/main` matched at foundation commit `87888dbe629ea7b481986e448f08ac1a2b6f65e2` after the initial push.
- Core CI [run 32758461898](https://github.com/DontHash/kyra-shelf-guard/actions/runs/32758461898): passed on Python 3.11 and 3.12.
- Issues and Projects enabled; wiki disabled; squash-only merges and automatic source-branch deletion enabled.
- Dependency alerts, automated security fixes, and read-only default workflow permissions enabled.
- Official GitHub actions updated to current immutable release commits after the first hosted run exposed Node-runtime deprecation warnings.

## Limitations and next action

Team reviewer handles remain unassigned; `@DontHash` is the temporary steward and CODEOWNER. GitHub returned HTTP 403 when branch protection was configured because protected branches for a private repository require upgrading the current account plan. Until that changes, agents must follow the documented PR workflow and CI, but GitHub cannot prevent an administrator from bypassing it.

Next: add Persons 1–4 to the roster/CODEOWNERS. After a GitHub plan upgrade, enforce the documented review and required-check policy on `main`.

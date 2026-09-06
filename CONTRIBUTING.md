# Contributing

Kyra uses four parallel owner workstreams with shared contracts and gated integration. Contributions are welcome only when they remain traceable, reviewable, and honest about evidence.

## Before work starts

1. Read `AGENTS.md` and complete its preflight.
2. Claim one issue with an owner (`P1`, `P2`, `P3`, or `P4`), requirement IDs, scope, non-scope, and acceptance evidence.
3. Check `docs/TEAM_OWNERSHIP.md` and `docs/CONTRACTS.md` before selecting files.
4. Branch from current `main` using `<owner>/<issue>-<slug>`.

Follow the command-level [Collaboration
Workflow](docs/COLLABORATION_WORKFLOW.md), including its normal branch, verified
commit, and push routine. Do not substitute a generic Git flow for the
repository's ownership, evidence, and history-safety rules.

Parallel work is coordinated by stable interfaces, not by copying logic between owner modules. If another workstream is not ready, use a versioned mock or replay fixture owned by Person 4.

## Local setup

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.lock
.\.venv\Scripts\python.exe -m pip install -e .
```

Install `requirements-simulation.lock` or `requirements-gpu.lock` only for work that needs it. Core tests must remain credential-free, offline, and CPU-compatible.

## Pull-request contents

Every implementation pull request must include:

- tests for success, failure, invalid input, and compatibility as applicable;
- commands actually run and their results;
- an updated owner status file under `docs/status/`;
- a work-item record under `docs/work-items/` based on `docs/templates/WORK_ITEM.md`;
- a changelog entry for notable behavior;
- all documentation selected by the matrix in `docs/DOCUMENTATION_POLICY.md`;
- contract proposal and approvals when a shared interface changes.

CI checks code, links, repository consistency, and whether changed files have the required documentation companions. Passing CI does not replace owner review or gate-specific evidence.

### Change-impact ownership

The `check_change_impact.py` classifier maps changed paths to owner status
requirements. The named Person 1 generation, conversion, and verification
scripts (`generate_golden_pack.py`, `convert_ocid.py`, `verify_person1.py`)
and the corresponding test names (`golden`, `midas`, `provenance`) classify as
Person 1 and do not count as governance changes. Every other `scripts/` and
`.github/` change remains Person 4 governance and requires the governance
companions. To add a future Person 1 script, extend `PERSON1_SCRIPTS` in
`scripts/check_change_impact.py` through a Person 4-reviewed change.

## Shared-contract changes

Do not edit `src/kyra/contracts.py`, the public manifest schema, units, coordinate frames, event meanings, or compatibility policy as an implementation shortcut.

Follow `docs/CONTRACT_CHANGE_PROCESS.md`: propose first, identify all consumers, define compatibility/migration and tests, obtain every affected owner approval, and have Person 4 merge the synchronized contract, mocks, docs, and tests. Unapproved proposals remain documents only.

## Review expectations

Reviewers verify:

- ownership and requirement traceability;
- smallest reasonable scope and no duplicated owner logic;
- units, timestamps, coordinate frames, and invalid-depth behavior;
- deterministic and offline behavior where required;
- success/failure/compatibility tests;
- documentation and status truth;
- provenance and licence obligations;
- evidence language that does not overclaim.

At least one non-author reviewer should approve normal code. Shared contracts require Person 4 plus every affected owner. Release evidence requires the relevant gate owners listed in `docs/INTEGRATION_GATES.md`.

## Required local checks

```powershell
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m compileall -q src tests scripts
.\.venv\Scripts\python.exe scripts\check_repo_consistency.py
.\.venv\Scripts\python.exe scripts\check_change_impact.py --base origin/main
```

Additional owner and gate checks are defined in `docs/TESTING.md` and the relevant plan.

## Merge and release policy

- Pull requests target `main` and should be squash-merged after required checks and approvals.
- Delete merged branches and do not commit directly to `main`. The current GitHub plan cannot server-enforce protected branches on a private repository, so every human and agent must follow this rule until protection is available; the limitation is tracked in WI-000.
- A package version is not a release by itself. Person 4 owns release notes, frozen commands, evaluation evidence, and tags after Gate 7.
- External data and generated bulk output are never merged.

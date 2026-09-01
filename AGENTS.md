# AGENTS.md

This is the mandatory operating contract for every coding agent in this repository. Do not implement first and reconcile documentation later.

## Documentation route

Start with docs/agents/README.md to find the smallest relevant technical document
set for the task. Files under docs/people/ are plain-English teammate summaries;
they do not replace approved decisions, contracts, specifications, tests, or
evidence records.

## Mandatory preflight

Before editing, an agent must:

1. Run `git status --short --branch` and preserve unrelated work.
2. If a remote exists, run `git fetch origin` and confirm the branch is based on current `origin/main`. Never pull across a dirty worktree.
3. Read `README.md`, `docs/PROJECT_CHARTER.md`, `docs/TEAM_OWNERSHIP.md`, `docs/PROJECT_STATUS.md`, `docs/DECISIONS.md`, and `docs/CONTRACTS.md`.
4. Read the relevant owner specification/plan, nearby implementation, tests, `docs/TESTING.md`, and `docs/DOCUMENTATION_POLICY.md`.
5. Run `python scripts/check_repo_consistency.py`. Resolve documentation drift before feature work.
6. Identify one GitHub issue/work-item ID, one accountable owner, the files in scope, the acceptance checks, and any affected contracts.
7. Confirm that no newer decision, proposal, owner status, or contract version supersedes the task.

If ownership or contract impact is ambiguous, stop and open a proposal; do not infer permission.

## Source-of-truth order

When sources disagree, use this order:

1. The controlling assignment DOCX.
2. Approved entries in `docs/DECISIONS.md` and approved contract-change records.
3. `docs/CONTRACTS.md`, owner specifications, and integration-gate definitions.
4. Tests and implemented behavior.
5. Plans, status files, README summaries, issues, and pull-request text.

Record a conflict instead of silently choosing the most convenient interpretation.

## Ownership boundaries

- **Person 1:** input data, deterministic simulation, calibration, baseline artifacts, dataset conversion, and provenance.
- **Person 2:** registration, signed depth change, occlusion-safe geometry, clustering, volume, and temporal change state.
- **Person 3:** replay/pretrained tracking, masks, proximity, authorization, and deterministic alert rules.
- **Person 4:** shared contracts, pipeline/orchestration, CLI, configuration, evaluation, CI, documentation integration, and release evidence.

The authoritative path matrix is `docs/TEAM_OWNERSHIP.md`. Tests follow the component owner. A downstream consumer may not edit its producer's module to bypass a contract.

Only Person 4 may merge a shared-contract change after approval from every affected owner. Until approval, add a proposal under `docs/contract-changes/`; do not change the public contract, schema meaning, units, coordinate frames, or compatibility behavior.

## Non-negotiable technical rules

- Use Python 3.12 locally while preserving `requires-python >=3.11` unless an approved decision changes it.
- Store depth as 16-bit PNG millimetres on disk and two-dimensional `float32` metres in memory.
- Treat zero, NaN, masked, or missing depth as unknown, never as empty shelf space.
- Use integer nanosecond timestamps in monotonic order.
- Keep the deterministic core independent of network access, CUDA, Blender, and downloaded assets.
- Derive randomness from the scenario seed; sort file lists and JSON keys where byte stability matters.
- Keep datasets, weights, generated batches, point clouds, and run output outside Git. Commit only tiny reviewed fixtures.
- Record source URL, version, checksum, licence, selected records, conversion command, and exclusions for external data.
- Say “suspicious shelf-removal alert,” not theft detection or proof of intent.
- Never report synthetic, mocked, tracker-only, local-only, or build-only evidence as real end-to-end evidence.

## Change workflow

Use the exact branch, commit, and push routine in
`docs/COLLABORATION_WORKFLOW.md`; repository policy overrides an agent's generic
Git habits.

1. Create or claim an issue using the work-item template.
2. Use a branch named `<owner>/<issue>-<slug>` such as `p2/41-occlusion-mask`.
3. Add or update the failing test/acceptance assertion first where practical.
4. Make the smallest change inside the owner boundary.
5. Run focused checks, then the required broad checks.
6. Update in the same branch:
   - `CHANGELOG.md` for notable behavior;
   - the applicable file under `docs/status/`;
   - one record under `docs/work-items/`;
   - specifications, contracts, decisions, testing, datasets, architecture, or integration gates when their truth changes.
7. Run the repository and change-impact validators.
8. Open a pull request with evidence and required owner approvals. Do not merge your own unreviewed contract change.

## Required checks

```powershell
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m compileall -q src tests scripts
.\.venv\Scripts\python.exe scripts\check_repo_consistency.py
.\.venv\Scripts\python.exe scripts\check_change_impact.py --base origin/main
```

Use the owner-specific proof in `docs/TESTING.md`. A successful unit suite does not close an integration gate unless that gate's exact evidence was also produced.

## Handoff and progress

Every meaningful pull request must leave enough durable context for the next agent:

- requirement/work-item ID and accountable owner;
- scope completed and explicit exclusions;
- files and contracts changed;
- commands actually run, environment, results, and saved evidence paths;
- risks, unresolved decisions, dependencies, and exact next action.

Use `docs/templates/HANDOFF.md` and update the relevant owner status file. Status values are `Not started`, `Ready`, `In progress`, `Blocked`, `In review`, or `Complete`; `Complete` requires linked evidence. Do not use status files as a substitute for tests.

## Git and safety

- Keep commits small and name requirement/work-item IDs where available.
- Never overwrite, reset, or delete another contributor's work.
- Never force-push `main`, commit secrets, or commit bulk/generated data.
- Ask before destructive actions, schema migrations, public API changes, or licence changes.
- Do not claim a push, check, approval, merge, deployment, or benchmark that did not actually happen.

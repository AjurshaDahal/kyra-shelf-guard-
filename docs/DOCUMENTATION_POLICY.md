# Documentation Policy and Impact Matrix

## Authority and conflict handling

Use the source order in `AGENTS.md`. When two sources disagree, create a work item that names both statements, the owners required to decide, and the temporary fail-closed behavior. Do not “fix” a conflict by changing only the easiest document.

Plans describe intended work. Status files describe the latest evidence-backed state. Tests describe verified behavior. A completed status or changelog line without evidence is drift.

## Required change companions

| Changed area | Must change in the same pull request |
|---|---|
| Any product code or test | `CHANGELOG.md`, applicable `docs/status/PERSON*.md`, and one `docs/work-items/*.md` record |
| Shared contract, manifest/config schema, public event/API | Above plus approved `docs/contract-changes/*.md`, `docs/CONTRACTS.md`, `docs/DECISIONS.md`, compatibility tests, and affected specs |
| Person 1 data/generator/baseline/converter | P1 status and implementation plan; also `DATASETS.md` for external data/provenance changes |
| Person 2 geometry/occlusion | P2 status, tests/evidence, and architecture when data flow changes |
| Person 3 tracking/rules | P3 status, tests/evidence, and architecture when data flow changes |
| Person 4 pipeline/CLI/evaluation | P4 status, integration gate/status, testing commands, and architecture as applicable |
| Dependency or Python compatibility | `requirements*.lock`/`pyproject.toml`, `DEVELOPMENT.md`, `TESTING.md`, changelog, and owner status |
| CI/governance/review policy | `.github/` or scripts plus `AGENTS.md`/`CONTRIBUTING.md`, changelog, P4 status, and work-item record |
| Dataset, asset, model, or licence | `DATASETS.md`/provenance, licence decision, tests, changelog, and relevant owner status |
| Integration gate completion | `PROJECT_STATUS.md`, a `docs/gates/GATE-<n>.md` evidence record, all named owner statuses, and changelog |
| New authoritative document | `README.md` documentation map when user-facing, and always `llms.txt` plus repository consistency requirements when mandatory |

`scripts/check_change_impact.py` enforces the mechanically detectable subset. Reviewers remain responsible for semantic impact.

## Status conventions

Allowed values are `Not started`, `Ready`, `In progress`, `Blocked`, `In review`, and `Complete`.

- `Blocked` names the external dependency or decision and the next unblock action.
- `Complete` links to commands/results and the merged commit.
- Dates use `YYYY-MM-DD`; timestamps use an explicit timezone when time matters.
- Planned commands and expected results are clearly labelled planned.
- Never replace a failed result with a planned success statement.

## Durable records

- `docs/status/`: current owner snapshots; update in place.
- `docs/work-items/`: one durable record per merged work item; do not delete after completion.
- `docs/contract-changes/`: proposals and approval/implementation history.
- `docs/gates/`: immutable evidence summary for completed integration gates.
- `docs/DECISIONS.md`: durable choices, not daily progress.
- `CHANGELOG.md`: user/team-visible notable changes, not every commit.

Large logs, datasets, recordings, reports, and generated arrays stay outside Git. Commit a small evidence record with checksum, command, environment, and durable storage location instead.

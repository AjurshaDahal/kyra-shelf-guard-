# Documentation Hub

This page is the map for the repository's documentation. Choose the path that
matches what you are trying to do; do not read every file in `docs/` first.

## Choose a starting path

| You are... | Start here | Then use |
|---|---|---|
| New to the project | [Plain-English team guide](people/README.md) | [Getting started](people/GETTING_STARTED.md) |
| A coding agent | [Agent documentation route](agents/README.md) | [AGENTS.md](../AGENTS.md) and the task-specific authority it names |
| Checking current progress | [Project status](PROJECT_STATUS.md) | The linked owner status and work-item records |
| Claiming or reviewing work | [Team ownership](TEAM_OWNERSHIP.md) | [Collaboration workflow](COLLABORATION_WORKFLOW.md) and [Contributing](../CONTRIBUTING.md) |
| Working on a shared interface | [Contract registry](CONTRACTS.md) | [Contract change process](CONTRACT_CHANGE_PROCESS.md) and an approved proposal |
| Checking whether a gate is complete | [Integration gates](INTEGRATION_GATES.md) | A matching record under [gates/](gates/) when the evidence exists |

## Authority by purpose

- **Mission and boundaries:** [Project Charter](PROJECT_CHARTER.md) and [System
  Requirements](SYSTEM_REQUIREMENTS.md).
- **Architecture and local development:** [Architecture](ARCHITECTURE.md) and
  [Development](DEVELOPMENT.md).
- **Interfaces and decisions:** [Contracts](CONTRACTS.md), [Decisions](DECISIONS.md),
  and [Contract Change Process](CONTRACT_CHANGE_PROCESS.md).
- **Tests and release evidence:** [Testing](TESTING.md), [Integration Gates](INTEGRATION_GATES.md),
  and completed records under [gates/](gates/).
- **Owner plans and specifications:** the applicable `PERSON*.md` document named
  by [Team Ownership](TEAM_OWNERSHIP.md).

When sources disagree, follow the source order in [AGENTS.md](../AGENTS.md): the
controlling assignment and approved decisions outrank summaries, plans, and
issue or pull-request text.

## Directory map

- [`people/`](people/): plain-English guides for teammates and non-specialists.
- [`agents/`](agents/): a task-based route for coding agents; it points to
  authority instead of copying it.
- [`status/`](status/): current evidence-backed snapshots, one per owner.
- [`work-items/`](work-items/): durable scope, verification, limitation, and
  handoff records for changes.
- [`contract-changes/`](contract-changes/): shared-interface proposals and
  approval history.
- [`gates/`](gates/): evidence records for completed integration gates only.
- [`templates/`](templates/): blank forms for handoffs, work items, and contract
  changes.
- Root-level `docs/*.md`: project authority that must keep its stable path so
  existing links and owner boundaries remain valid.

## Keeping the map trustworthy

Update the authoritative technical document first, then update affected
summaries and this map when a starting path changes. Keep planned work clearly
labelled as planned. Before opening a pull request, run the checks listed in
[Testing](TESTING.md) and the repository consistency validator.

# WI-010 — Audience-Specific Documentation

- **Owner:** P4
- **Status:** In review
- **Started:** 2026-08-30
- **Completed:** N/A
- **Requirements:** Documentation governance
- **Integration gate:** None

## Objective

A teammate can understand Kyra's purpose, limits, current progress, and joining
steps in plain English, while a coding agent has a separate route to the existing
technical authority.

## In scope

- Human-first repository README.
- Plain-English guides under docs/people/.
- Agent technical route under docs/agents/.
- One authoritative normal branch, commit, and push routine linked from the
  agent and teammate routes.
- Documentation hub and GitHub issue-template link for repository navigation.
- Documentation authority, indexes, validation, current project snapshot,
  changelog, and Person 4 status needed to keep the split durable.

## Out of scope

- Product code and owner algorithms.
- Shared runtime contracts, schema meanings, units, or compatibility behavior.
- Completing an integration gate or claiming end-to-end/T4 evidence.
- Rewriting every existing technical document.

## Inputs, outputs, and contracts

Inputs are the current charter, ownership matrix, decisions, contract registry,
status/evidence records, tests, and documentation policy. Outputs are documentation
and a consistency-validator requirement. No runtime contract is affected.

## Implementation summary

The root README now gives a short project explanation and routes readers by
audience. docs/README.md maps the people, agent, authority, status, work-item,
contract-change, gate, and template paths. docs/people/ explains progress, roles,
terms, and joining steps in plain English. docs/agents/ routes coding agents to
authoritative files by task. The documentation policy defines how summaries stay
subordinate and synchronized, and repository consistency requires the entry
pages.

Contributors now have one command-level Git routine in the collaboration guide.
It covers starting or synchronizing an issue branch, reviewing and explicitly
staging a coherent diff, committing with owner/work-item context, pushing without
rewriting shared history, and keeping merge approval separate from push access.

## Documentation impact

- README.md, docs/README.md, docs/people/*, and docs/agents/README.md: audience
  entry paths.
- AGENTS.md, llms.txt, and docs/DOCUMENTATION_POLICY.md: routing and authority.
- docs/COLLABORATION_WORKFLOW.md, CONTRIBUTING.md, and docs/DEVELOPMENT.md:
  authoritative Git procedure and links from adjacent contributor guidance.
- docs/PROJECT_STATUS.md, docs/CONTRACTS.md, the contract-change index, and the
  P-005 proposal header: current shared truth.
- .github/ISSUE_TEMPLATE/config.yml: GitHub filing route.
- docs/status/PERSON4.md, CHANGELOG.md, and this record: durable context.

## Verification

| Environment | Command | Result | Evidence |
|---|---|---|---|
| Windows, Python 3.12.7 | .venv\Scripts\python.exe -m pytest -q before edits | 52 passed | Local terminal, 2026-08-30 |
| Windows, Python 3.12.7 | .venv\Scripts\python.exe scripts\check_repo_consistency.py | Passed | Local terminal, 2026-08-30 |
| Windows, Python 3.12.7 | .venv\Scripts\python.exe scripts\check_change_impact.py --base origin/main | Passed for 17 changed files | Local terminal, 2026-08-30 |
| Windows, Python 3.12.7 | .venv\Scripts\python.exe -m ruff check . | Passed | Local terminal, 2026-08-30 |
| Windows, Python 3.12.7 | .venv\Scripts\python.exe -m compileall -q src tests scripts | Passed | Local terminal, 2026-08-30 |
| Windows, Python 3.12.7 | .venv\Scripts\python.exe -m pytest -q after edits | 52 passed | Local terminal, 2026-08-30 |
| Windows, Python 3.12.7 | git diff --cached --check | Passed | Local terminal, 2026-08-30 |
| Windows, Python 3.12.7 | .venv\Scripts\python.exe -m pytest | 83 passed | Local terminal, 2026-09-01 |
| Windows, Python 3.12.7 | .venv\Scripts\python.exe -m ruff check . | Passed | Local terminal, 2026-09-01 |
| Windows, Python 3.12.7 | .venv\Scripts\python.exe -m compileall -q src tests scripts | Passed | Local terminal, 2026-09-01 |
| Windows, Python 3.12.7 | .venv\Scripts\python.exe scripts\check_repo_consistency.py | Passed | Local terminal, 2026-09-01 |
| Windows, Python 3.12.7 | .venv\Scripts\python.exe scripts\check_change_impact.py --base origin/main | Passed for 19 changed files | Local terminal, 2026-09-01 |
| Windows | git diff --check | Passed | Local terminal, 2026-09-01 |

## Risks, limitations, and failures

- The people progress summary must be updated whenever its linked technical truth
  changes; automated validation cannot judge wording.
- Person 1-owned plan/status text still describes the now-approved P-005 proposal
  as approval-gated. Person 1 must synchronize those files before implementing
  P-005; this change does not cross that owner boundary.
- Issue #10 was initially created without the `work-item` label because the label
  did not exist; the repository label is now created and the issue is labelled.

## Handoff

Person 4/reviewer should confirm the plain-English status against technical records
and review the agent route for source-precedence accuracy. Person 1 should
separately update their plan/status when claiming P-005 implementation.

## Final links

- Issue: https://github.com/DontHash/kyra-shelf-guard/issues/10
- Pull request: https://github.com/DontHash/kyra-shelf-guard/pull/11
- Commits: 47bdc6d, 8913c40, and 2edca93 (documentation restructure series)

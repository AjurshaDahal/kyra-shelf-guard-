# Collaboration Workflow

## Goal

Allow four humans or AI agents to work in parallel without losing interface, status, decision, or evidence consistency. GitHub issues and pull requests coordinate active work; repository documents preserve durable truth.

## 1. Synchronize and orient

Each agent starts with the `AGENTS.md` preflight. Fetch the remote, work from current `main`, inspect open contract proposals and the relevant owner status, then run repository consistency validation. If documentation is already inconsistent, fix or report that drift before feature development.

## 2. Claim one work item

Create an issue from `.github/ISSUE_TEMPLATE/work-item.yml` with:

- one accountable owner and requirement IDs;
- problem, scope, non-scope, inputs, outputs, and contracts;
- acceptance commands/evidence;
- dependent issues and integration gate;
- documentation impact.

Only one active issue owns a file-level objective. Related work uses linked issues rather than duplicating implementation.

## 3. Branch without shared-state ambiguity

Use `<owner>/<issue>-<slug>`. Commit only files for that work item. Do not mix formatting, dependency upgrades, refactors, and feature behavior unless the issue explicitly includes them.

When parallel work depends on an unfinished owner:

- consume the frozen contract and Person 4-owned mock/replay fixture;
- do not copy the missing owner's algorithm;
- record the dependency in the issue and owner status;
- merge integration only after the producer's acceptance evidence exists.

## 4. Implement inside the boundary

Read the owned module, tests, relevant spec, and current contracts before editing. Add the smallest test that exposes the requirement, implement the narrow change, and exercise failure and compatibility paths.

Shared contract needs trigger `docs/CONTRACT_CHANGE_PROCESS.md`. A proposal may be prepared in parallel, but dependent production implementation waits for approval and the frozen version.

## 5. Maintain durable context in the same branch

An implementation change is incomplete until it includes:

1. `CHANGELOG.md` when behavior is notable.
2. The owner's file in `docs/status/` with current, evidence-backed state.
3. A record in `docs/work-items/` based on `docs/templates/WORK_ITEM.md`.
4. Every document selected by `docs/DOCUMENTATION_POLICY.md`.
5. Actual commands/results and evidence locations; never predicted results.

Status files are snapshots. Work-item records are the append-only audit trail. Pull-request conversation is not the sole home for a durable decision.

## 6. Verify in layers

Run focused tests first, then the full required suite, Ruff, byte-compilation, repository consistency, and change-impact validation. Run optional GPU/simulation/data checks only in the correct environment and label them separately.

Record:

- commit SHA;
- operating system and Python version;
- dependency lock or environment identity;
- exact command and exit result;
- fixture/dataset and checksum where relevant;
- whether evidence is unit, synthetic, public-data, integrated, or target-T4.

## 7. Review and merge

The pull-request template is mandatory. Review checks ownership, contracts, tests, documentation, status, provenance, and claim language. Normal code needs a non-author review when team handles are configured. Shared contracts need Person 4 and every affected owner.

CI must pass on the reviewed commit. Prefer squash merge to `main`, delete the branch, and ensure the issue/work-item record points to the final pull request/commit.

## 8. Handoff

The author leaves the next exact action, open risks, dependencies, and evidence using `docs/templates/HANDOFF.md`. Person 4 updates project-level gate state only after independently checking that the gate's exit criteria are met.

## Conflict protocol

If two branches touch the same contract or authoritative document:

1. Pause the later merge.
2. Rebase on current `main` and read the newly landed decision/status.
3. Re-evaluate the issue's scope and contract compatibility.
4. Resolve semantic differences with the named owners; do not mechanically choose both versions.
5. Rerun all impacted checks and update evidence after resolution.

## Automation boundary

Automation can fail a pull request for missing companions, broken links, inconsistent control files, tests, or lint. It cannot infer owner approval, scientific validity, licence compatibility, real-world performance, or whether an integration result is honest. Those remain explicit reviewed evidence.

# Documentation Route for Coding Agents

This is the technical entry point for agents. It routes tasks to existing
authoritative documents; it does not replace them.

The pages under docs/people/ are plain-English teammate summaries. They are useful
for explaining the project, but they are not contracts, approval records, or
implementation authority.

## Required reading order

1. Follow the complete preflight in [AGENTS.md](../../AGENTS.md).
2. Confirm mission and evidence language in the [Project Charter](../PROJECT_CHARTER.md).
3. Confirm path ownership in [Team Ownership](../TEAM_OWNERSHIP.md).
4. Check current truth in [Project Status](../PROJECT_STATUS.md) and the applicable
   file under [owner status](../status/README.md).
5. Check choices in [Decisions](../DECISIONS.md).
6. Check shared interfaces in [Contracts](../CONTRACTS.md) and the
   [Contract Change Process](../CONTRACT_CHANGE_PROCESS.md).
7. Read the relevant specification, implementation, tests, [Testing](../TESTING.md),
   and [Documentation Policy](../DOCUMENTATION_POLICY.md).

The controlling assignment and the source-precedence order in AGENTS.md govern
conflicts.

## Route by task

| Task | Read next |
|---|---|
| Person 1 input, simulation, calibration, baseline, or data | [Person 1 Specification](../PERSON1_SPEC.md), [Person 1 Plan](../PERSON1_IMPLEMENTATION_PLAN.md), and [Dataset Rules](../DATASETS.md) |
| Person 2 geometry or volume | [Architecture](../ARCHITECTURE.md), [Contracts](../CONTRACTS.md), Person 2 status, and nearby tests |
| Person 3 tracking or alert rules | [Architecture](../ARCHITECTURE.md), [Contracts](../CONTRACTS.md), Person 3 status, and nearby tests |
| Person 4 pipeline, CLI, evaluation, CI, or docs | [Integration Gates](../INTEGRATION_GATES.md), [Collaboration Workflow](../COLLABORATION_WORKFLOW.md), Person 4 status, and governance tests |
| Shared format or public interface | [Contract Change Process](../CONTRACT_CHANGE_PROCESS.md), approved proposals, affected owner statuses, and compatibility tests |
| Progress or handoff | Applicable owner status, [work-item records](../work-items/README.md), gate evidence, and actual test output |
| Branching, committing, pushing, or merging | [Collaboration Workflow](../COLLABORATION_WORKFLOW.md), especially the normal branch and verified-checkpoint commands |

## Keep the audiences synchronized

When technical truth changes, update its authoritative document first. Update an
affected plain-English summary in the same pull request. Translate the meaning
and limitation; do not copy schemas, version rules, or long test details into
docs/people/.

Never use a summary to override a decision, contract, test, owner specification,
or evidence record. If they disagree, record the conflict and correct the summary.

Every meaningful change still requires one issue, one owner, a scoped branch,
focused and broad checks, the applicable status update, a work-item record, and
the companions selected by [Documentation Policy](../DOCUMENTATION_POLICY.md).
Agents are expected to know how Git works, but they must not improvise the
repository-specific commit, push, history-rewrite, or merge policy.

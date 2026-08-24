# Contract Change Process

Shared interfaces allow the four owners to work independently. A contract change is therefore a coordinated project change, not a local refactor.

## What counts as a contract change

- Adding, removing, renaming, or reinterpreting a public field.
- Changing dtype, shape, units, coordinate frame, timestamp semantics, invalid values, required/optional status, enum values, serialization, checksum, or version policy.
- Changing a public import, CLI output consumed by another module, manifest/config schema, mock, or persisted artifact format.
- Changing an alert/event meaning or threshold ownership.

## Process

1. **Propose.** Copy `docs/templates/CONTRACT_CHANGE.md` to `docs/contract-changes/CC-<issue>-<slug>.md`. Do not edit implementation yet.
2. **Impact.** List every producer, consumer, owner, test, fixture, persisted artifact, documentation page, and integration gate affected.
3. **Design compatibility.** State old/new examples, version change, read/write policy, migration, rollback, deprecation window, and deterministic checksum implications.
4. **Review.** Person 4 and every affected owner records `Approve`, `Request changes`, or `Not affected` with date and rationale in the proposal/pull request.
5. **Freeze.** Person 4 assigns the contract version and merge order after approvals. A proposal marked pending is not implementation authority.
6. **Implement atomically.** Land schema/code, producer and consumer tests, mocks, registry, decision/status/changelog updates, and migration in the approved order.
7. **Verify.** Run compatibility tests for every producer/consumer and the affected integration gate. Save exact evidence.
8. **Close.** Mark the proposal implemented with commit/PR links. Keep the record; never rewrite history to hide the prior version.

## Approval matrix

| Change | Required approvals |
|---|---|
| `FramePacket`, baseline, scenario manifest | Person 4, Person 1, and every consuming owner affected |
| Geometry event | Person 4, Person 2, Persons 3/4 as consumers, plus Person 1 if input assumptions change |
| Track/mask/alert event | Person 4, Person 3, and Persons 2/4 as affected consumers |
| Runtime configuration | Person 4 plus every owner whose behavior/threshold is represented |
| Evaluation/report schema | Person 4 plus owners whose metrics/evidence are represented |

Silence is not approval. An AI agent cannot invent an approval or infer it from a passing test.

## Emergency incompatibility

There is no production emergency path in the current university prototype. If a critical defect is found, fail closed, record the unsupported version/input, and use the same approval process. Do not silently reinterpret stored evidence.

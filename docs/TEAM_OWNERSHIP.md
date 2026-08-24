# Team Ownership and Boundaries

This file translates the controlling four-person assignment into an operational touch/no-touch map. “Owner” means accountable for design, implementation, tests, documentation, and handoff. It does not permit unilateral shared-contract changes.

## Team roster

| Role | GitHub handle | Repository responsibility |
|---|---|---|
| Repository steward / temporary Person 4 delegate | `@DontHash` | Repository settings, CODEOWNERS, initial integration foundation |
| Person 1 | To be assigned | Data, simulation, calibration, baseline, provenance |
| Person 2 | To be assigned | Geometry, differencing, occlusion, volume |
| Person 3 | To be assigned | Tracking, proximity, authorization, alert rules |
| Person 4 | To be assigned | Contracts, pipeline, CLI, evaluation, CI, release |

Update this table and `.github/CODEOWNERS` together as soon as handles are known. Role labels in documents are not valid GitHub reviewers by themselves.

## Person 1 — Data and baseline

**Owns:** scenario ingestion, deterministic generation, calibration, baseline build/persistence, dataset conversion, provenance, and tiny golden fixtures.

**Primary current/future paths:**

- `src/kyra/io.py`, `src/kyra/baseline.py`;
- future Person 1 modules under `src/kyra/data/`, `src/kyra/simulation/`, and `src/kyra/calibration/` if P-001 approves that layout;
- `scenario-fixtures/`, dataset conversion scripts, provenance records;
- `docs/PERSON1_*`, `docs/DATASETS.md`, `docs/status/PERSON1.md`;
- corresponding Person 1 tests.

**Produces:** replayable scenarios, `FramePacket`, `BaselineArtifact`, shelf/calibration configuration, checksums, provenance.

**Must not implement:** registration/change geometry, person tracking, authorization/alert rules, orchestration, final evaluation, or shared-schema changes. Person 1 may propose manifest/contract changes but cannot implement them before approval.

## Person 2 — Geometry and change

**Owns:** camera registration/drift checks, signed depth differencing, invalid-depth handling, occlusion safety, shelf-frame projection, 3D clustering, volume estimation, and temporal geometry persistence.

**Primary future paths:**

- `src/kyra/geometry/`, `src/kyra/differencing/`, `src/kyra/occlusion/`;
- Person 2 configuration owned through Person 4's versioned config surface;
- Person 2 tests and `docs/status/PERSON2.md`.

**Consumes:** `FramePacket`, `BaselineArtifact`, shelf configuration, and Person 3 masks through frozen contracts.

**Produces:** `VolumeChangeEvent` with signed change type, affected shelf region/cluster, volume, time range, persistence, confidence/quality, and provenance as approved by the shared schema.

**Must not implement:** identity/tracking, authorization policy, final alerts, pipeline retries, CLI, or evaluation. Person 2 must never treat unknown/occluded depth as removal evidence.

## Person 3 — Tracking and alert rules

**Owns:** deterministic replay tracks, optional lazily loaded pretrained tracking adapter, aligned person masks, shelf proximity, authorization state, two-second association window, and deterministic alert-rule evaluation.

**Primary future paths:**

- `src/kyra/tracking/`, `src/kyra/proximity/`, `src/kyra/rules/`;
- Person 3 tests and `docs/status/PERSON3.md`.

**Consumes:** RGB-D frame timing/geometry, shelf configuration, `VolumeChangeEvent`, system mode, and authorized IDs through frozen contracts.

**Produces:** `PersonTrack`, aligned occlusion/person masks, and `AlertEvent`.

**Must not implement:** metric volume estimation, shared-contract ownership, pipeline orchestration, or final evaluation. The optional model path must not be required by deterministic core tests.

## Person 4 — Integration and evaluation

**Owns:** shared contracts, manifest/configuration schemas, mocks and compatibility fixtures, bounded orchestration, CLI, evaluation, CI, documentation integration, integration-gate evidence, releases, and final reporting.

**Primary current/future paths:**

- `src/kyra/contracts.py`, `src/kyra/manifest.py`, future `src/kyra/pipeline/`, `src/kyra/evaluation/`, `src/kyra/cli.py`;
- `.github/`, repository governance scripts, shared configs;
- integration/evaluation tests, `docs/CONTRACTS.md`, gate records, and `docs/status/PERSON4.md`.

**Produces:** versioned shared interfaces/mocks, bounded integrated runs, five CLI commands, frozen split/evaluation reports, comparison results, and release evidence.

**Must not implement:** duplicate geometry, tracking, or data algorithms inside the pipeline. Person 4 coordinates owner outputs and returns failures to the responsible owner.

## Shared and protected surfaces

| Surface | Merge authority | Required consultation |
|---|---|---|
| `src/kyra/contracts.py` and public schema meaning | Person 4 | Every producer and consumer affected |
| `src/kyra/manifest.py` public fields/version | Person 4 | Person 1 plus every consuming owner |
| Versioned runtime configuration | Person 4 | Owners of every affected parameter |
| `.github/`, CI, release policy | Person 4/steward | All owners when required checks or workflow change |
| Assignment, project charter, licence, system claim | Project owner + Person 4 | All owners |
| `docs/DECISIONS.md` | Decision owner recorded in entry | All affected owners |
| `docs/PROJECT_STATUS.md` | Person 4 integrates | Each owner updates only their supported truth |

## Cross-owner change rule

When one work item needs files from another owner:

1. Split the work into separate owner-scoped issues where possible.
2. Name one lead and the required reviewers in both issues.
3. Change contracts through the proposal process, not through a mixed implementation pull request.
4. Merge producer contract/mocks before consumer implementation unless an approved coordinated rollout explicitly says otherwise.
5. Update both owner status files only with evidence each owner can support.

An agent may review any workstream but edits only the workstream assigned in its issue unless the issue explicitly records cross-owner approval.

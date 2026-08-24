# Kyra Shelf Guard

Kyra is a four-workstream university project for detecting suspicious shelf removals from replayable RGB-D input. It measures persistent physical shelf change and associates that evidence with nearby, non-authorized person tracks. It does **not** identify theft, infer intent, or require a product-specific model for every SKU.

The repository is the shared source of truth for code, frozen contracts, decisions, work status, evidence, and handoffs. Development is intentionally split into parallel owner modules with explicit integration gates.

## Current truth

The Person 1 foundation is the only implemented product workstream today: shared data objects, strict scenario manifests, RGB-D replay, baseline construction and persistence, and MiDaS anchor alignment exist. The deterministic generator, golden pack, dataset converter, geometry path, tracking/rules path, integration pipeline, evaluation harness, and CLI remain planned or unimplemented.

The verified local foundation result is 35 passing tests plus Ruff on Python 3.12.7. This is not an end-to-end or target-T4 result. See [Project Status](docs/PROJECT_STATUS.md) for the live workstream and gate ledger.

## Four workstreams

| Owner | Owns | Produces | Does not own |
|---|---|---|---|
| Person 1 — Data and baseline | Replay input, deterministic simulation, calibration, baseline, dataset conversion, provenance | `FramePacket`, `BaselineArtifact`, scenarios | Geometry differencing, tracking, alert policy, orchestration |
| Person 2 — Geometry | Registration, signed depth change, occlusion-safe clustering, volume and temporal geometry state | `VolumeChangeEvent` | Person identity/tracking, authorization, final alert policy |
| Person 3 — Tracking and rules | Replay tracks, optional YOLO/ByteTrack adapter, proximity, authorization, deterministic alert rule | `PersonTrack`, masks, `AlertEvent` | Geometry volume estimation, shared-contract ownership, evaluation |
| Person 4 — Integration | Shared contracts, bounded pipeline, CLI, configuration, evaluation, CI, release evidence | Integrated runs, reports, frozen interfaces | Reimplementing owner algorithms inside orchestration |

The detailed touch/no-touch matrix is in [Team Ownership](docs/TEAM_OWNERSHIP.md). Shared contracts may be merged only by Person 4 after every affected owner approves the proposal.

## Collaboration contract

Every human or AI contributor must:

1. Read [AGENTS.md](AGENTS.md), [Project Status](docs/PROJECT_STATUS.md), [Decisions](docs/DECISIONS.md), and the relevant owner specification before editing.
2. Start from current `main`, work from one issue/work-item ID, and stay inside the named owner boundary.
3. Propose shared-contract changes before implementing them.
4. Add tests and truthful evidence for the changed behavior.
5. Update the owner status file, work-item record, changelog, and any affected authoritative documentation in the same pull request.
6. Pass code, documentation-link, repository-consistency, and change-impact checks before merge.

The full process is in [Collaboration Workflow](docs/COLLABORATION_WORKFLOW.md). CI enforces the documentation impact rules; it does not treat a plan, build, or synthetic run as proof of an end-to-end result.

## Quick setup on Windows

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.lock
.\.venv\Scripts\python.exe -m pip install -e .
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe scripts\check_repo_consistency.py
```

Do not run `kyra` yet: `pyproject.toml` declares the future entry point, but `src/kyra/cli.py` is not implemented.

## Documentation map

### Project control

- [Project Charter](docs/PROJECT_CHARTER.md) — mission, non-goals, evidence language, and definition of done.
- [Team Ownership](docs/TEAM_OWNERSHIP.md) — four roles, file boundaries, reviewers, and handoff obligations.
- [Collaboration Workflow](docs/COLLABORATION_WORKFLOW.md) — issue-to-merge workflow for humans and agents.
- [Project Status](docs/PROJECT_STATUS.md) — current workstream and integration-gate snapshot.
- [Integration Gates](docs/INTEGRATION_GATES.md) — entry, exit, and evidence required for Gates 1–7.

### Contracts and change control

- [Contract Registry](docs/CONTRACTS.md) — current producers, consumers, schemas, and freeze state.
- [Contract Change Process](docs/CONTRACT_CHANGE_PROCESS.md) — proposal, approval, compatibility, and rollout protocol.
- [Documentation Policy](docs/DOCUMENTATION_POLICY.md) — source precedence and change-impact matrix.
- [Decisions](docs/DECISIONS.md) — locked and pending durable choices.

### Engineering and Person 1

- [Architecture](docs/ARCHITECTURE.md), [Development](docs/DEVELOPMENT.md), [Testing](docs/TESTING.md), and [Dataset Rules](docs/DATASETS.md).
- [Person 1 Specification](docs/PERSON1_SPEC.md) and [Implementation Plan](docs/PERSON1_IMPLEMENTATION_PLAN.md).
- [Contributing](CONTRIBUTING.md), [Changelog](CHANGELOG.md), [AI index](llms.txt), and [Project Skills](SKILLS.md).

## Assignment and licence

The controlling source is [Four-Person Physics-Based Shelf Removal Detection Plan](Four-Person_Physics-Based_Shelf_Removal_Detection_Plan.docx). If a repository summary conflicts with it, stop, record the conflict, and correct the summary through review.

Code is licensed `AGPL-3.0-only`; see [LICENSE](LICENSE). Dataset, asset, and model licences are reviewed separately, and bulk datasets, generated runs, weights, and point clouds must stay outside Git.

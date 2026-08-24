# Project Capability and Evidence Map

This is a project capability map, not a list of agent plugins or packages. Each skill belongs to one owner and is complete only with the named evidence.

| Owner | Capability | Main output | Minimum proof |
|---|---|---|---|
| P1 | RGB-D replay and validation | `FramePacket` sequence | Valid replay plus malformed asset/schema tests |
| P1 | Deterministic scenarios | Scenario manifest/assets/golden pack | Same seed produces byte-identical canonical output |
| P1 | Calibration and baseline | Saved `BaselineArtifact` | 30-frame fusion, fixed/portable behavior, checksum/reload |
| P1 | Metric fallback and data conversion | Aligned approximate depth; converted scenarios/provenance | Anchor success/failure tests; offline converter fixture and licence/checksum record |
| P2 | Registration and signed change | Registered depth difference | Known transform/drift and addition/removal assertions |
| P2 | Occlusion-safe 3D geometry | Persistent `VolumeChangeEvent` | Unknown/occluded suppression, clusters, known-volume error |
| P3 | Replay/pretrained tracking | `PersonTrack` and aligned masks | Deterministic replay; lazy optional adapter; alignment failures |
| P3 | Proximity, authorization, and rule | `AlertEvent` | Time-window, authorized-restock, alert/no-alert matrix |
| P4 | Contracts and mocks | Frozen schemas/configuration/fixtures | Producer-consumer compatibility and version rejection tests |
| P4 | Bounded pipeline and CLI | Integrated run and five commands | Clean-environment vertical scenarios and failure behavior |
| P4 | Evaluation and release | Frozen reports, comparison, tagged evidence | Reproducible metrics, target-T4 record, claim/licence audit |

## Shared collaboration skills

Every owner must be able to:

- trace work to requirement, issue, owner, contract version, and integration gate;
- distinguish plans from implemented behavior and local/synthetic evidence from end-to-end evidence;
- update status, work-item, changelog, tests, and affected authority together;
- review interface units, shapes, coordinate frames, timestamps, invalid values, and compatibility;
- record exact commands, environment, checksums, outcomes, limitations, and the next action;
- hand work to another owner without relying on private chat history.

## Optional tools

Open3D, BlenderProc, Torch, pretrained tracking, and MiDaS inference are adapters or extended evidence. They do not become core CI dependencies and must be loaded only in the owner path that needs them.

See [Team Ownership](docs/TEAM_OWNERSHIP.md), [Testing](docs/TESTING.md), and [Integration Gates](docs/INTEGRATION_GATES.md) for authority and acceptance detail.

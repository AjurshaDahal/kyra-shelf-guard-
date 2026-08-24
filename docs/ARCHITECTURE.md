# Architecture

## Purpose

Kyra separates replay/calibration, physical geometry, human context, and integration so each owner can test independently. Versioned contracts and Person 4-owned mocks connect the modules; the pipeline does not reach into private owner logic.

## System flow

```text
P1: scenario/data -> FramePacket + BaselineArtifact
                         |                |
                         v                v
                 P3: tracks/masks    P2: registered,
                         |            occlusion-safe 3D change
                         |                |
                         |                v
                         +-------> VolumeChangeEvent
                                      |
                                      v
                         P3: proximity + authorization + rule
                                      |
                                      v
                                  AlertEvent
                                      |
                                      v
                         P4: bounded pipeline, CLI, evaluation
```

Person 2 consumes Person 3 masks for occlusion safety; Person 3 consumes Person 2 geometry events for association. Those two paths must use frozen timestamps, frame IDs, shelf coordinates, masks, and event contracts to avoid a circular implementation dependency.

## Owner modules

| Owner | Current/future package surfaces | Boundary output |
|---|---|---|
| P1 | `kyra.io`, `kyra.baseline`, future data/simulation/calibration/converter modules | `FramePacket`, `BaselineArtifact`, replay fixtures/provenance |
| P2 | future `kyra.geometry`, `kyra.differencing`, `kyra.occlusion` | `VolumeChangeEvent` |
| P3 | future `kyra.tracking`, `kyra.proximity`, `kyra.rules` | `PersonTrack`, aligned masks, `AlertEvent` |
| P4 | `kyra.contracts`, `kyra.manifest`, future pipeline/evaluation/CLI/config | versioned interfaces, integrated outputs, reports |

P-001 still controls whether future modules are packages or single files. Do not reorganize working imports until Person 4 records the approved layout and migration.

## Current implemented foundation

| Module | Implemented responsibility | Important public surface |
|---|---|---|
| `kyra.contracts` | Shared array/event foundations | `FramePacket`, `BaselineArtifact`, `ShelfConfig`, `VolumeChangeEvent`, `PersonTrack`, `AlertEvent` |
| `kyra.manifest` | Strict scenario JSON and canonical checksum | `ScenarioManifest`, load/write/checksum functions |
| `kyra.io` | Replayable scenario input | `ScenarioFrameSource` / `FrameSource` |
| `kyra.baseline` | Baseline build/persistence and anchor alignment | `BaselineBuilder`, save/load, `MidasAnchorAligner` |

No P2/P3 algorithm, integrated pipeline, evaluation harness, or CLI exists yet.

## Parallel-development seam

For every frozen contract, Person 4 supplies a tiny deterministic mock/replay fixture. Owners develop against that fixture and publish conformance tests. The real producer replaces the mock only at the relevant integration gate. This supports parallel work without duplicating producer behavior.

The pipeline uses bounded queues/timeouts and explicit failure states. It passes versioned objects between owner adapters and records configuration/provenance; it never hides missing evidence by manufacturing defaults.

## Data rules at boundaries

- RGB: lossless PNG on disk; `uint8` RGB array in memory.
- Depth: `uint16` millimetres on disk; two-dimensional `float32` metres in memory.
- Invalid/occluded depth: unknown and excluded from removal evidence.
- Masks: lossless PNG or boolean arrays aligned to a named frame.
- Timestamps: monotonic integer nanoseconds.
- Camera intrinsics: 3 × 3; camera-to-shelf transform: 4 × 4.
- Volumes: cubic metres with explicit threshold/configuration provenance.
- Baseline: compressed NPZ arrays plus readable JSON metadata and checksum.

## Trust and evidence boundaries

- MiDaS is approximate and accepted only after metric shelf anchors pass; it never silently replaces metric depth.
- Optional pretrained tracking provides observations, not intent or guilt.
- Person-correlated removal is a suspicious event requiring review, not theft proof.
- Synthetic fixtures test deterministic behavior; public data expands coverage; only a complete frozen run is end-to-end evidence.
- Large artifacts remain outside Git with checksums, commands, provenance, and durable locations recorded.

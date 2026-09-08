# Architecture

## Purpose

Kyra separates replay/calibration, physical geometry, human context, and integration so each owner can test independently. Versioned contracts and Person 4-owned mocks connect the modules; the pipeline does not reach into private owner logic.

## System flow

```text
P1: scenario/data -> FramePacket + BaselineArtifact
                         |                |
                         v                v
              P3: YOLO boxes + RGB-D  P2: registered,
                  -> localized tracks, occlusion-safe 3D change
                     proximity/masks       |
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
                    P4: pipeline, CLI, evaluation, local review UI
```

Person 2 consumes Person 3 masks for occlusion safety; Person 3 consumes Person 2 geometry events for association. Those two paths must use frozen timestamps, frame IDs, shelf coordinates, masks, and event contracts to avoid a circular implementation dependency.

## Owner modules

| Owner | Current/future package surfaces | Boundary output |
|---|---|---|
| P1 | `kyra.io`, `kyra.baseline`, future data/simulation/calibration/converter modules | `FramePacket`, `BaselineArtifact`, replay fixtures/provenance |
| P2 | future `kyra.geometry`, `kyra.differencing`, `kyra.occlusion` | `VolumeChangeEvent` |
| P3 | future `kyra.tracking`, `kyra.proximity`, `kyra.rules` | `PersonTrack`, aligned masks, `AlertEvent` |
| P4 | `kyra.contracts`, `kyra.manifest`, `kyra.pipeline`, `kyra.cli`, `kyra.simulator` | versioned interfaces, integrated outputs, reports, local visual review |

The approved P-001 layout keeps one distributable `kyra` package rooted at
`src/kyra`. Future modules live under `kyra` or appropriate `kyra/<area>/`
subpackages; assignment-named top-level packages are not created, and existing
`kyra.*` public imports remain stable.

## Current implemented foundation

| Module | Implemented responsibility | Important public surface |
|---|---|---|
| `kyra.contracts` | Shared array/event foundations | `FramePacket`, `BaselineArtifact`, `ShelfConfig`, `VolumeChangeEvent`, `PersonTrack`, `AlertEvent` |
| `kyra.manifest` | Strict scenario JSON and canonical checksum | `ScenarioManifest`, load/write/checksum functions |
| `kyra.io` | Replayable scenario input | `ScenarioFrameSource` / `FrameSource` |
| `kyra.baseline` | Baseline build/persistence and anchor alignment | `BaselineBuilder`, save/load, `MidasAnchorAligner` |
| `kyra.tracking.rgbd_localization` | Fail-closed metric localization of person boxes from aligned RGB-D | `localize_tracks_from_rgbd` |
| `kyra.pipeline` | Deterministic real-owner scenario orchestration | `run_scenario` |
| `kyra.cli` | Five assignment commands and reviewed scenario profiles | `kyra` / `main` |
| `kyra.simulator` | Loopback-only visual replay of synthetic cases | `run_example_case`, local HTTP review UI |

The candidate vertical slice now uses the implemented P1/P2/P3 components. The
visual simulator is a P4 review surface over the same deterministic scenario
profiles and pipeline; it is not a second detection implementation and does not
turn synthetic evidence into camera or real-world proof.

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
- Person-box localization uses robust inner-box median depth rather than
  instance segmentation. Unknown or insufficient depth cannot assert shelf
  proximity, and the box can still include background or carried objects.
- Person-correlated removal is a suspicious event requiring review, not theft proof.
- Synthetic fixtures test deterministic behavior; public data expands coverage; only a complete frozen run is end-to-end evidence.
- Large artifacts remain outside Git with checksums, commands, provenance, and durable locations recorded.

# Architecture

## Purpose

Person 1 turns raw or generated shelf scenes into two stable things the rest of the team can trust:

1. A replayable stream of RGB-D frames.
2. A saved opening baseline of the shelf.

## System flow

```text
procedural generator ─┐
BlenderProc adapter ──┼─> scenario folder ─> ScenarioFrameSource ─> FramePacket
OCID converter ───────┘          │                                      │
                                 │                                      ├─> Person 2: geometry change
                                 │                                      ├─> Person 3: human context
                                 └─> first 30 clear frames ─> BaselineBuilder
                                                              │
                                                              └─> BaselineArtifact
                                                                      │
                                                                      ├─> Person 2
                                                                      └─> Person 4 pipeline
```

MiDaS is an isolated fallback. It may supply aligned approximate depth only after shelf anchors pass calibration. It must never silently replace metric RGB-D data.

## Current modules

| Module | Current responsibility | Important public surface |
|---|---|---|
| `kyra.contracts` | Shared types and array validation | `FramePacket`, `BaselineArtifact`, `ShelfConfig`, enums and team events |
| `kyra.manifest` | Strict scenario JSON models | `ScenarioManifest`, `load_manifest`, `write_manifest`, `manifest_checksum` |
| `kyra.io` | Scenario replay | `ScenarioFrameSource`, alias `FrameSource` |
| `kyra.baseline` | Baseline building and persistence | `BaselineBuilder`, `save_baseline`, `load_baseline`, `MidasAnchorAligner` |

## Planned Person 1 additions

The assignment describes ownership by responsibility. This repository already keeps reading and calibration behavior in `io.py` and `baseline.py`, so the implementation plan extends those tested modules instead of moving working code merely to match assignment folder labels:

```text
src/kyra/
├── simulation.py           # lightweight deterministic generator
├── ocid.py                 # pure OCID conversion logic
└── cli.py                  # future shared command routing, coordinated with Person 4

scripts/
├── generate_golden_pack.py
├── convert_ocid.py
└── verify_person1.py

scenario-fixtures/
└── golden/                 # ten tiny deterministic scenarios
```

Existing `io.py`, `manifest.py`, and `baseline.py` receive only test-driven changes. Before adding or moving package files, confirm that Person 4 agrees with keeping the single-package layout. The shared contract shapes must not change merely to match the folder names shown in the assignment.

## Boundary rules

- Person 1 produces `FramePacket` and `BaselineArtifact` values.
- Person 2 consumes them and produces `VolumeChangeEvent`.
- Person 3 produces `PersonTrack` and applies human context.
- Person 4 owns shared contract changes, orchestration, CLI integration, evaluation, and final reporting.

## Data rules at module boundaries

- RGB: lossless PNG on disk; `uint8` RGB array in memory.
- Depth: `uint16` millimetres on disk; `float32` metres in memory.
- Invalid depth: zero or masked on disk; always marked unknown in memory.
- Masks: lossless PNG and boolean arrays in memory.
- Timestamps: integer nanoseconds, monotonically increasing.
- Camera intrinsics: 3 × 3 matrix.
- Camera-to-shelf transform: 4 × 4 matrix.
- Baseline: compressed NPZ arrays plus JSON metadata.

## Design trade-offs

The core generator uses simple procedural shapes instead of depending on BlenderProc. This makes unit tests fast and repeatable on Windows and the T4 environment, but the scenes look less realistic. BlenderProc and scanned assets remain extended evidence for visual and geometry diversity.

Large data stays outside Git. This keeps the repository usable, but it means every external dataset needs a reproducible download/location record, checksum, conversion command, and provenance manifest.

# Shared Contract Registry

Person 4 owns this registry and shared implementation surfaces. Producers and consumers own conformance tests. A registry entry marked “foundation” exists but is not automatically frozen for every future consumer.

## Contract rules

- Timestamps are integer nanoseconds and monotonic within a replay.
- Depth on disk is uint16 millimetres; depth in memory is 2-D `float32` metres.
- Zero, NaN, masked, or absent depth is unknown.
- Array shape, dtype, coordinate frame, and mutability expectations are explicit and tested.
- Schemas use version identifiers and deterministic canonical serialization where checksums matter.
- Consumers reject unsupported major versions and unknown meanings; they do not guess.
- Shared changes follow [Contract Change Process](CONTRACT_CHANGE_PROCESS.md).

## Registry

| ID | Contract | Current surface | Producer | Consumers | State |
|---|---|---|---|---|---|
| C-001 | Frame packet | `src/kyra/contracts.py::FramePacket` | Person 1 | Persons 2, 3, 4 | Foundation implemented |
| C-002 | Baseline artifact | `src/kyra/contracts.py::BaselineArtifact` | Person 1 | Persons 2, 4 | Foundation implemented |
| C-003 | Volume change event | `src/kyra/contracts.py::VolumeChangeEvent` | Person 2 | Persons 3, 4 | Type foundation only; producer absent |
| C-004 | Person track | `src/kyra/contracts.py::PersonTrack` | Person 3 | Persons 2, 3, 4 | Type foundation only; producer absent |
| C-005 | Alert event | `src/kyra/contracts.py::AlertEvent` | Person 3 | Person 4 | Type foundation only; producer absent |
| C-006 | Scenario manifest | `src/kyra/manifest.py::ScenarioManifest` | Person 1 data, Person 4 schema | Persons 1–4 | Version 1.0 foundation |
| C-007 | Shelf/runtime config | Planned versioned schema | Person 4 with owner input | Persons 1–4 | Not defined |
| C-008 | Pipeline/evaluation result | Planned | Person 4 | Reporting/evaluation | Not defined |

## Current freeze notes

- Existing foundation tests protect current array normalization, invalid-depth handling, schema validation, canonical manifest checksum, replay ordering, and persistence behavior.
- C-003 through C-005 have no real owner producer yet; downstream code must use explicit mocks and must not claim integrated validation.
- Manifest 1.1 object-mask and shape-family fields are proposed in `P1-02_CONTRACT_CHANGE_PROPOSAL.md` but remain unapproved and unimplemented.
- P-001 package layout remains pending; paths may be reorganized only through an approved decision that preserves public imports or defines migration.

## Compatibility evidence required

Each frozen contract needs:

1. producer serialization/construction tests;
2. consumer loading/validation tests;
3. invalid, missing, and unsupported-version rejection tests;
4. canonical fixture/checksum where persisted;
5. unit/coordinate/timestamp examples;
6. backward/forward compatibility policy;
7. one Person 4-owned mock or tiny replay fixture.

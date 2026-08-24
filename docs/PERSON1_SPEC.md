# Person 1 Specification

**Status:** Ready for team review  
**Owner:** Person 1  
**Source of truth:** `Four-Person_Physics-Based_Shelf_Removal_Detection_Plan.docx`

## Goal in simple words

Person 1 gives the rest of the team trustworthy shelf data. The data must replay the same way every time, use clear physical units, describe missing depth honestly, and include a saved picture of the shelf before anything changes.

## What Person 1 owns

- Reading recorded RGB-D shelf scenarios.
- Making small, repeatable synthetic scenarios.
- Preparing a ten-scenario golden test pack.
- Building and saving the opening shelf baseline from 30 clear frames.
- Separating fixed shelf structure from portable objects smaller than 0.5 m³.
- Converting approved OCID examples into the common scenario format.
- Aligning MiDaS depth to known shelf distances, or rejecting it when alignment is unreliable.
- Recording sources, licences, checksums, selections, and exclusions.
- Supplying tests and an independent handoff report.

## What Person 1 does not own

- Person tracking or pose estimation.
- Final 3D change detection and removal confirmation.
- Alert policy, authorization rules, or final reports.
- Shared contract changes without Person 4 review.
- Proving the complete four-person system works from camera to alert.

## Required inputs and outputs

| Item | Comes from | Person 1 responsibility |
|---|---|---|
| RGB PNG frames | Generator or approved dataset | Read as colour images without lossy conversion |
| 16-bit depth PNG frames | Generator or approved dataset | Convert millimetres to metres |
| Valid-depth masks | Generator or dataset conversion | Keep invalid depth marked unknown |
| Occlusion masks and track annotations | Generator or Person 3 fixtures | Preserve and expose them for replay |
| Camera and shelf calibration | Scenario or calibration step | Validate matrix shapes and shelf bounds |
| Scenario manifest | Generator or converter | Validate paths, timestamps, schema, and expected result |
| `FramePacket` stream | Person 1 | Hand to downstream processing |
| `BaselineArtifact` | Person 1 | Save once and reload without calibration |
| Provenance record | Person 1 | Show source, checksum, licence, selection, and exclusions |

## Functional requirements

### Input and replay

| ID | Requirement | Completion proof |
|---|---|---|
| P1-IO-001 | A scenario folder contains a strict manifest plus lossless RGB, depth, and mask files. Relative paths resolve from the manifest folder. | Valid fixture loads on Windows and T4. |
| P1-IO-002 | Depth stored as unsigned 16-bit millimetres becomes `float32` metres in memory. Zero, NaN, or masked values remain unknown. | Unit tests check conversion and invalid pixels. |
| P1-IO-003 | Reject missing files, wrong depth type, mismatched image sizes, duplicate frame IDs, unordered timestamps, missing baseline frames, and invalid calibration shapes. | One focused failure test per validation rule. |
| P1-IO-004 | Replay exposes baseline frames, event frames, occlusion masks, and track annotations without silently changing shared `FramePacket` fields. | Contract test exercises every accessor. |

### Deterministic scenarios

| ID | Requirement | Completion proof |
|---|---|---|
| P1-SIM-001 | The core generator works without network, CUDA, Blender, or external datasets. | Clean CPU test environment generates the pack. |
| P1-SIM-002 | The same seed and settings write byte-identical manifests; relative paths and ordering are stable across runs. | Generate twice into separate folders and compare bytes and asset hashes. |
| P1-SIM-003 | Cover no change, removal, addition, person-only occlusion, post-removal occlusion, authorized restocking, lighting variation, invalid depth, and camera drift. | Frozen ten-scenario matrix is complete. |
| P1-SIM-004 | Each scenario records seed, change time, object mask, object volume, category, shape family, and expected alert result. | Schema and golden-pack audit pass. |
| P1-SIM-005 | Procedural coverage includes envelopes or trays, cylinders, irregular shoes, and handled or hanging objects. | Scenario metadata and rendered masks show all families. |
| P1-SIM-006 | BlenderProc and approved scanned-object assets are optional realism adapters, not core-test dependencies. | Core suite passes with these packages absent. |

### Public data and provenance

| ID | Requirement | Completion proof |
|---|---|---|
| P1-DATA-001 | OCID archives and converted bulk data stay outside Git and are checked with SHA-256 before use. | Provenance record contains local name, source URL, size, and checksum. |
| P1-DATA-002 | The OCID converter preserves frame order and calibration, maps depth and masks into Kyra’s format, and can reverse an addition sequence to form a removal case when valid. | Tiny converter fixture and selected real-data smoke test pass. |
| P1-DATA-003 | Every included or excluded source records licence, attribution, selected subset, conversion command, and reason for exclusion where relevant. | Provenance review has no blank required fields. |

### Calibration and baseline

| ID | Requirement | Completion proof |
|---|---|---|
| P1-CAL-001 | Build the baseline from at least 30 clear frames using median depth and a per-pixel noise estimate. | A 29-frame test rejects; a 30-frame test succeeds. |
| P1-CAL-002 | Fixed shelf structure is never returned as a portable component. Objects smaller than 0.5 m³ are eligible as portable components. | Known synthetic structure and object tests pass. |
| P1-CAL-003 | Build a shelf occupancy grid with a default 1 cm cell size and reject unsafe grid dimensions. | Shape, occupied-cell, and safety-limit tests pass. |
| P1-CAL-004 | Save arrays and metadata with schema version and calibration checksum; reload them without recalculating the baseline. | Round-trip equality test and a no-recompute test pass. |
| P1-CAL-005 | On synthetic objects of at least 0.5 litres, baseline volume error is at most 10%. | Parameterized known-volume acceptance test passes. |

### MiDaS fallback

| ID | Requirement | Completion proof |
|---|---|---|
| P1-MIDAS-001 | Align relative inverse depth only when at least two distinct metric shelf anchors are present and residual error is within the agreed limit. | Good-anchor test passes; missing, repeated, or inconsistent anchors reject. |
| P1-MIDAS-002 | Mark accepted output as approximate and exclude it from primary metric-volume results unless calibration succeeds. | Artifact metadata and evaluation selection test pass. |

### Handoff and acceptance

| ID | Requirement | Completion proof |
|---|---|---|
| P1-QA-001 | The frozen ten-scenario golden pack loads on Windows and the target T4 environment. | Two environment reports record commands, versions, and results. |
| P1-QA-002 | All Person 1 unit, contract, determinism, conversion, and baseline acceptance tests pass without network access. | Saved full-suite output and exit code 0. |
| P1-QA-003 | An independent teammate can follow the setup, load the pack and baseline, and reproduce the stated results. | Signed handoff report using the provided template. |

## Ten-scenario golden pack

The assignment asks for ten scenarios but lists nine behavior groups. The second removal case below is a provisional interpretation and needs team confirmation before the pack is frozen.

| # | Scenario | Expected result | Main extra condition |
|---:|---|---|---|
| 1 | No change | No alert | Stable tray or envelope |
| 2 | Removal: regular thin item | Alert | Envelope or tray |
| 3 | Removal: irregular item | Alert | Shoe or handled/hanging object; provisional tenth case |
| 4 | Addition | No removal alert | Cylinder |
| 5 | Person-only occlusion | No alert | Shelf contents unchanged |
| 6 | Removal followed by occlusion | Alert after enough visible evidence | Occlusion must not erase the removal |
| 7 | Authorized restocking | No suspicious alert | `RESTOCK_MODE` or authorized annotation |
| 8 | Lighting variation | No alert | RGB changes while metric depth stays stable |
| 9 | Invalid-depth region | No alert from unknown pixels | Missing depth overlaps shelf area |
| 10 | Camera drift | Reject or suppress result | Transform exceeds accepted registration limit |

## Quality rules

- Core acceptance must be offline and CPU-first.
- All units, coordinate systems, timestamps, and unknown values must be explicit.
- Generated evidence must include its seed and tool version.
- A source file existing is not proof that its behavior has passed.
- No final accuracy or T4 claim may be made without a saved test report.

## Required handoff package

1. Scenario reader and deterministic generator.
2. Frozen ten-scenario golden pack.
3. Baseline builder plus save/load files.
4. OCID converter and provenance manifest.
5. MiDaS anchor-alignment adapter.
6. Person 1 tests and results.
7. Independent handoff report.

The build order and exact file-level work are in [PERSON1_IMPLEMENTATION_PLAN.md](PERSON1_IMPLEMENTATION_PLAN.md).

# Integration Gates

Gates are ordered evidence boundaries, not calendar milestones. A gate is complete only when every exit criterion passes against recorded schemas, configuration, fixtures, commands, and commit SHA.

## Gate 1 — Contract compatibility

**Owners:** Person 4 accountable; Persons 1–3 approve affected surfaces.

**Exit:** frozen versions for `FramePacket`, `BaselineArtifact`, `VolumeChangeEvent`, `PersonTrack`, `AlertEvent`, scenario manifest, and the five-field shelf/configuration boundary (`shelf_id`, `roi_xyxy`, `bounds_min_m`, `bounds_max_m`, `voxel_size_m`); executable mocks/fixtures for every producer and consumer; units, coordinate frames, timestamps, invalid values, serialization, and compatibility tested; pending proposals either approved or explicitly excluded; C-007 v1 is approved and frozen.

**Current status:** complete for the shared contract-compatibility layer based on the repository’s frozen definitions, compatibility tests, and deterministic Person 4 mocks. This is a compatibility gate only; it does not claim real Person 1/2/3 algorithm completion. Real geometry, tracking, baseline-generation, and end-to-end validation remain in Gates 2–5 and are not represented by these mocks.

**Evidence record:** `docs/gates/GATE-1.md` contains the current reviewed evidence summary for the frozen surfaces and the mock-based compatibility proof.

## Gate 2 — Data and baseline

**Owner:** Person 1; Person 4 validates consumption.

**Entry:** Gate 1 contracts required by Person 1 are frozen.

**Exit:** deterministic same-seed scenario output, all ten reviewed golden scenarios, malformed/valid replay proof, 30-frame baseline and persistence/checksum proof, fixed/portable behavior, MiDaS anchor failure policy, offline converter fixture plus provenance, Windows and target-T4 load evidence.

## Gate 3 — Geometry

**Owner:** Person 2; Persons 1 and 3 validate inputs/masks; Person 4 validates output contract.

**Entry:** Gate 1 and suitable Gate 2 fixtures.

**Exit:** registration/drift thresholds, signed addition/removal behavior, unknown-depth rejection, occlusion suppression, 3D cluster persistence, known-volume accuracy, deterministic `VolumeChangeEvent` serialization, and failure-path evidence.

## Gate 4 — Tracking and rules

**Owner:** Person 3; Persons 1 and 2 validate timing/mask geometry; Person 4 validates event contract.

**Entry:** Gate 1, replay frames/tracks, and representative geometry events.

**Exit:** deterministic replay tracking, lazy optional pretrained adapter, frame-aligned masks, shelf proximity, authorization suppression, two-second association window, deterministic alert/no-alert matrix, and serialized `PersonTrack`/`AlertEvent` evidence.

## Gate 5 — Complete vertical pipeline

**Owner:** Person 4; all owners approve their integrated behavior.

**Entry:** Gates 1–4 complete on one compatible schema/configuration set.

**Exit:** bounded pipeline queues/timeouts/failure states; no duplicated owner algorithms; planned five CLI commands operate in a clean core environment; at least one no-change, removal, occlusion, authorized restock, invalid-depth, and drift scenario runs through all applicable stages; outputs link to source events and configuration.

## Gate 6 — Frozen evaluation

**Owner:** Person 4; owners validate component metrics.

**Entry:** Gate 5 complete and evaluation split/config frozen before scoring.

**Exit:** immutable evaluation selection/checksums, metric definitions, thresholds, comparison baselines, saved command/configuration, reproducible reports, failure analysis, and separate labels for synthetic/public/approximate evidence. No tuning on frozen evaluation outcomes.

## Gate 7 — Performance and release

**Owner:** Person 4/release owner; all owners sign off.

**Entry:** Gate 6 complete.

**Exit:** target-T4 run using reviewed SHA and frozen commands; resource/performance measurements with environment details; clean-clone setup and five-command smoke test; licence/provenance review; security/secrets check; final report/whitepaper claim audit; changelog/version/tag/remote SHA agreement.

## Evidence record

For every completed gate, add `docs/gates/GATE-<n>.md` containing:

- reviewed commit SHA and contract/config versions;
- owners and approvals;
- exact commands and environment;
- fixture/dataset identifiers and checksums;
- expected and actual results;
- known limitations and excluded claims;
- links to durable artifacts that are not committed when too large.

Do not create a gate record with fabricated or planned results.

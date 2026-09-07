# Person 3 Status — Tracking, Proximity, and Alert Rules

- **Status:** Complete
- **Last updated:** 2026-09-09

## Implemented

Person 3 owns the tracking, shelf-proximity, and removal-alert rule layer.

Implemented and verified:

- deterministic replay tracking through `ReplayTracker`
- reconstruction of `PersonTrack` objects from scenario annotations
- shelf proximity calculation using metric 3D position and shelf AABB geometry
- `last_near_timestamp_ns` tracking
- bounding-box-based person occlusion masks
- deterministic removal-alert association
- two-second person/removal association window
- newest eligible person-track selection
- authorized-person suppression
- `RESTOCK_MODE` suppression
- minimum missing-volume threshold
- deterministic alert IDs
- frozen rule version `P3-001`
- empty-pose normalization for replay tracks
- serialized `PersonTrack` and `AlertEvent` evidence
- deterministic synthetic Gate 4 evidence generation (`scripts/generate_person3_gate4_evidence.py`)
- SHA-256 evidence manifest

## Active

Person 3 component implementation and deterministic evidence are complete.

The remaining work is integration-level rather than a missing Person 3 component implementation.

## Blocked or pending

Gate 4 exit criteria are compiled in `docs/gates/GATE-4.md` (record under Person 4 review). The following integration-level items remain outside the owner's deterministic evidence but are tracked:

- lazy optional pretrained detector/tracking adapter (optional path; not required by the deterministic core per D-002)
- live detector/tracker integration
- upstream depth/3D position integration
- upstream volume-change integration (real `VolumeChangeEvent` chain from Person 2's `ShelfGeometryProvider`, replacing the synthetic events used in evidence)
- required cross-owner Gate 4 validation and approvals

## Next

- Person 4 review of `docs/gates/GATE-4.md` and the gate status decision.
- Re-run the Gate 4 evidence after live upstream integrations are available, and validate the real Person 2 -> Person 3 chain at Gate 5.
- Coordinate with the relevant owners on the remaining integration-level items.

## Evidence

- Evidence generator: `scripts/generate_person3_gate4_evidence.py` (integrated via pull request #70, commit `0452c2e`).
- Generated evidence directory: `evidence/person3-gate4/` (git-ignored by design; the reproducible generator is committed instead).
- Evidence includes `person3-track-001.json`, `person3-alert-001.json`, `person3-gate4-matrix.json`, the deterministic scenario, and `SHA256SUMS.txt`.

Representative deterministic outcome (frozen environment, 2026-09-09):

- Track ID: `7`; near shelf: `True`; last near timestamp: `2000000000 ns`
- Alert ID: `alert-p3-g4-removal-001-track-7`; rule version: `P3-001`
- Matrix cases: eligible-removal -> alert; authorized-person, restock-mode, below-minimum-volume, outside-two-second-window, addition-direction -> no alert (all asserted)

Merged-tree verification (Windows, Python 3.12.7, requirements.lock pins):

- Person 1/2/3/4 full repository suite: 195 passed
- Ruff, byte-compilation, repository-consistency, and change-impact checks passed
- Evidence generator rerun produced an identical SHA-256 manifest (deterministic regeneration)

Configuration and contract versions:

- runtime schema version: `1.0`
- scenario manifest version: `1.1`
- Person 3 rule version: `P3-001`
- association window: `2 seconds`
- minimum alert volume: `5e-5 m³`
- shelf proximity threshold: `1.0 m`

Limitations:

- replay tracking uses deterministic scenario annotations rather than a live detector/tracker
- metric person position is supplied by the scenario fixture; Person 3 does not estimate depth
- person occlusion is currently represented using track bounding boxes rather than instance segmentation
- the removal alert is a human-review signal and does not establish theft, intent, or identity
- the two-second association window is fixed by the current rule configuration
- synthetic evidence is representative component evidence and is not production deployment validation
- the Gate 4 matrix uses synthetic `VolumeChangeEvent` inputs; the real Person 2 -> Person 3 chain is validated at Gate 5
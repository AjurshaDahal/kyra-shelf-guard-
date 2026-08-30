# CC-006 — Scenario manifest object metadata and reader API

- **Status:** Implemented
- **Proposer:** Person 1
- **Person 4 owner:** Person 4 / repository steward
- **Contract/version:** runtime `SCHEMA_VERSION` remains `"1.0"`; manifest version `1.0 -> 1.1`
- **Issue/PR:** P-005 approval record in `docs/P1-02_CONTRACT_CHANGE_PROPOSAL.md`

## Problem and non-goals

The existing manifest records scenario seed, event timing, object volume, category, and alert expectations, but it does not preserve the per-frame object mask or the object shape family in a machine-readable form. The manifest also lacks a public reader access path for retrieving the object mask, even though the scenario reader already exposes track annotations and occlusion masks.

This change does not alter the shared runtime dataclass contract. `FramePacket` remains unchanged, and the runtime `SCHEMA_VERSION` remains `"1.0"`.

## Current and proposed examples

Current manifest behavior:

```json
{
  "schema_version": "1.0",
  "frames": [{
    "frame_id": "frame-0002",
    "timestamp_ns": 2000000000,
    "rgb_path": "rgb/frame-0002.png",
    "depth_path": "depth/frame-0002.png"
  }],
  "ground_truth_events": [{
    "change_type": "REMOVAL",
    "first_seen_timestamp_ns": 2000000000,
    "volume_m3": 0.05,
    "should_alert": true
  }]
}
```

Approved and implemented manifest behavior:

```json
{
  "schema_version": "1.1",
  "frames": [{
    "frame_id": "frame-0002",
    "timestamp_ns": 2000000000,
    "rgb_path": "rgb/frame-0002.png",
    "depth_path": "depth/frame-0002.png",
    "object_mask_path": "masks/frame-0002-object.png"
  }],
  "ground_truth_events": [{
    "change_type": "REMOVAL",
    "first_seen_timestamp_ns": 2000000000,
    "volume_m3": 0.05,
    "shape_family": "cylinder",
    "should_alert": true
  }]
}
```

Reader API:

```python
source.object_mask(frame_id) -> np.ndarray
```

Behavior:
- reads a boolean object mask when `object_mask_path` exists;
- returns all-false mask with depth shape when no object mask is present;
- rejects wrong dimensions with a clear `ValueError`;
- preserves the repository’s file-not-found and path-safety behavior.

## Producer/consumer impact

| Owner | Surface | Required change | Compatibility test |
|---|---|---|---|
| Person 1 | `src/kyra/manifest.py` | Add version-aware manifest support and validator rules | manifest load/validate tests |
| Person 1 | `src/kyra/io.py` | Add `object_mask(frame_id)` reader, matching mask semantics | replay and mask IO tests |
| Person 4 | Shared contract registry | Update manifest registry and decision records | repository consistency and change-impact checks |
| Person 2 | Consumption | Confirmed not affected | existing downstream contract remains unchanged |
| Person 3 | Consumption | Confirmed not affected | existing downstream contract remains unchanged |

## Compatibility, migration, and rollback

- Supported manifest versions are `{"1.0", "1.1"}`.
- New writes use manifest version 1.1.
- Version 1.0 remains readable and validated.
- Unsupported manifest versions are rejected.
- Runtime `SCHEMA_VERSION` remains `"1.0"`; no change is made to runtime `FramePacket` or any other dataclass contract.
- The object-mask path and shape family are manifest-only metadata for scenario validation and replay, not runtime event transport.
- Rollback is limited to manifest-version compatibility; old 1.0 manifests still load, and runtime consumers remain unaffected.

## Required synchronized updates

- C-006 implementation in `src/kyra/manifest.py` and `src/kyra/io.py`.
- Contract registry update in `docs/CONTRACTS.md`.
- Decision sync in `docs/DECISIONS.md`.
- Owner status updates in `docs/status/PERSON1.md` and `docs/status/PERSON4.md`.
- Changelog entry in `CHANGELOG.md`.
- Work-item record in `docs/work-items/WI-006-manifest-object-mask.md`.
- Repository governance checks and test evidence.

## Approval record

| Owner | Decision | Date | Rationale/link |
|---|---|---|---|
| Person 4 | Approved | 2026-08-26 | `docs/P1-02_CONTRACT_CHANGE_PROPOSAL.md` |
| Person 2 | Not affected | 2026-08-30 | Confirmed that the P-005 manifest changes do not require runtime/consumer contract changes. |
| Person 3 | Not affected | 2026-08-30 | Confirmed that the P-005 manifest changes do not require runtime/consumer contract changes. |

## Implementation evidence

- Approved P-005 proposal: `docs/P1-02_CONTRACT_CHANGE_PROPOSAL.md`
- Targeted validation: `python -m pytest tests/test_manifest.py tests/test_io.py -q` — 26 passed.
- Full validation: `python -m pytest -q` — 62 passed.
- Governance validation: `python scripts/check_repo_consistency.py` — passed.
- Governance validation: `python scripts/check_change_impact.py --base HEAD` — passed after synchronized governance updates.

# P1-02 Contract Change Proposal

**Status:** Approved; implementation pending
**Owners:** Person 1 and Person 4
**Scope:** Scenario manifest and replay reader only
**Requirements:** P1-IO-004 and P1-SIM-004

## Why this change is needed

The current manifest already records the scenario seed, first change timestamp,
object volume, category, and expected alert result. It does not have named fields
for the per-frame object mask or the object's shape family. Putting those values
in free-text notes would make the golden pack hard to validate.

The existing manifest already stores track annotations, but the reader has no
public method for retrieving them. That reader-only gap can be fixed without
changing the shared `FramePacket` contract.

## Proposed manifest version 1.1

Keep loading existing version 1.0 manifests. New generated scenarios use version
1.1 and add these fields:

| Model | Field | Meaning |
|---|---|---|
| `FrameRecord` | `object_mask_path: str | None` | Relative path to a lossless binary mask for the object involved in the event. `None` is allowed only for version 1.0 compatibility or scenarios with no object. |
| `GroundTruthEvent` | `shape_family: ShapeFamily | None` | One of `thin_box_or_tray`, `cylinder`, `irregular`, or `handled_or_hanging`. `None` is allowed only for version 1.0 compatibility or events with no object. |

Use the existing fields rather than adding duplicates:

| Required fact | Existing field |
|---|---|
| Seed | `ScenarioManifest.random_seed` |
| Change time | `GroundTruthEvent.first_seen_timestamp_ns` |
| Object volume | `GroundTruthEvent.volume_m3` |
| Category | `ScenarioManifest.category` |
| Expected alert | `GroundTruthEvent.should_alert` |

## Version 1.1 validation rules

- Version 1.0 remains readable so current valid fixtures do not break.
- Version 1.1 object events must name a `shape_family`.
- Version 1.1 frames covering an object event must name an
  `object_mask_path`; a no-change or person-only frame may omit it.
- Object-mask paths follow the same relative-path and folder-boundary rules as
  RGB, depth, and occlusion masks.
- The reader checks that object-mask dimensions match depth dimensions and
  returns a boolean mask.
- Unknown manifest fields remain rejected.
- `FramePacket` is unchanged.

## Reader API

The unblocked reader work uses the data already present in version 1.0:

```python
source.track_annotations(frame_id) -> tuple[TrackAnnotation, ...]
```

After this proposal is approved, add:

```python
source.object_mask(frame_id) -> np.ndarray
```

When a frame has no object mask, `object_mask` returns an all-false mask with the
same height and width as depth, matching the current occlusion-mask behavior.

## Compatibility and ownership

- Person 1 owns the manifest implementation, reader methods, fixtures, and
  tests.
- Person 4 approves the shared on-disk format and confirms whether the shared
  `SCHEMA_VERSION` constant accepts both 1.0 and 1.1 or is split into current and
  supported versions.
- No downstream runtime dataclass changes are proposed.
- The golden pack is not frozen until this decision and the tenth-scenario shape
  decision are approved.

## Approval checklist

- [x] Person 4 approves the two fields and their locations.
- [x] Person 4 approves the four `ShapeFamily` names.
- [x] Person 4 approves backward loading of version 1.0 and generation of
  version 1.1.
- [x] Person 2 — Not affected — 2026-08-30. Confirmed that the proposed
  P-005 manifest changes do not require changes to their runtime/consumer
  contracts. Proceed.
- [x] Person 3 — Not affected — 2026-08-30. Confirmed that the proposed
  P-005 manifest changes do not require changes to their runtime/consumer
  contracts. Proceed.
- [x] Person 4 approval date and reviewer are recorded below.

**Approved by:** Person 4
**Approval date:** 2026-08-26
**Requested changes:** None recorded yet

**Person 2 confirmation:** Not affected — 2026-08-30. Confirmed that the
proposed P-005 manifest changes do not require changes to their
runtime/consumer contracts. Proceed.

**Person 3 confirmation:** Not affected — 2026-08-30. Confirmed that the
proposed P-005 manifest changes do not require changes to their
runtime/consumer contracts. Proceed.

**Person 4 versioning decision:** Use `MANIFEST_SCHEMA_VERSION = "1.1"` with
supported manifest versions `{"1.0", "1.1"}`. Read both versions, write version
1.1, reject unsupported versions, and leave the shared runtime
`SCHEMA_VERSION` unchanged. Persons 2 and 3 have both confirmed "Not affected"
on 2026-08-30 for the current P-005 proposal.

## Implementation after approval

1. Add the version and fields to `src/kyra/manifest.py`.
2. Add version-aware validation and old-fixture compatibility tests.
3. Add `object_mask(frame_id)` to `src/kyra/io.py` with missing, wrong-size,
   and outside-folder tests.
4. Update the Person 1 specification and changelog with the approved decision.
5. Start P1-03 only after the updated manifest contract passes all checks.

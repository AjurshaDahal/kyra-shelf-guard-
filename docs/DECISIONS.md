# Project Decisions

This log records durable choices. It is not a work diary. Change a locked decision only with the owners named below, then update the specification, plan, tests, and changelog together.

## Locked decisions

### D-001 — CPU-first deterministic core

- **Decision:** Core Person 1 tests and the golden pack must run without network, CUDA, Blender, or external datasets.
- **Why:** Both Windows and target T4 checks must be repeatable and easy to diagnose.
- **Trade-off:** Core scenes are simpler than full rendered scenes.
- **Source:** Assignment Person 1 objective.

### D-002 — Heavy tools are adapters

- **Decision:** BlenderProc, Google Scanned Objects, OCID, Open3D, and full MiDaS inference are optional or integration paths.
- **Why:** They add realism or coverage but must not make basic tests fragile.
- **Trade-off:** Extra integration commands and provenance records are required.
- **Source:** Assignment Person 1 responsibilities.

### D-003 — Python 3.12 on this laptop

- **Decision:** Use Python 3.12 for local development while preserving package compatibility with Python 3.11 and later.
- **Why:** Python 3.12 is installed locally and fits the current optional-library compatibility range better than the default Python 3.13.
- **Trade-off:** Windows commands use `py -3.12` instead of the default `python` launcher target.

### D-004 — Lossless, inspectable scenario storage

- **Decision:** Store RGB and masks as PNG, depth as 16-bit PNG millimetres, and metadata as strict JSON.
- **Why:** Files stay inspectable and depth values are not silently changed by video compression.
- **Trade-off:** Scenario folders contain more files than a video-based format.
- **Source:** Frozen assignment contract and current code.

### D-005 — Invalid depth is unknown

- **Decision:** Zero, NaN, or masked depth never means free shelf space.
- **Why:** Treating missing sensor data as empty space would create false removal evidence.
- **Source:** Frozen assignment contract.

### D-006 — Baseline is reusable evidence

- **Decision:** Save baseline arrays in NPZ and human-readable metadata in JSON, both tied to a schema version and calibration checksum.
- **Why:** Downstream work must load the same baseline without recalibrating.
- **Source:** Assignment and current implementation.

### D-007 — MiDaS stays explicitly approximate

- **Decision:** MiDaS output is accepted only after at least two consistent metric shelf anchors and is marked `approximate_metric`.
- **Why:** Raw MiDaS depth has unknown scale and shift.
- **Trade-off:** Some footage must be rejected instead of producing a confident volume.

### D-008 — External data stays outside Git

- **Decision:** Commit scripts, checksums, selections, licences, and tiny fixtures; do not commit full datasets or bulk generated output.
- **Why:** Repository size and data-licence obligations remain manageable.

### D-009 — Ten-scenario golden pack composition

- **Decision:** Cover the assignment’s nine named behaviours and use a second removal shape family as the tenth scenario.
- **Why:** The assignment asks for ten scenarios but names nine behaviour groups.
- **Trade-off:** The second removal case is a planning interpretation and must be confirmed with the team before the golden pack is frozen.
- **Status:** Provisional until team confirmation.

### D-010 — Private GitHub collaboration repository

- **Decision:** Keep the canonical repository private on GitHub with `main` as
  the default integration branch, issue-scoped feature branches, pull-request
  review, squash merge, and automated code/documentation governance checks.
- **Why:** The team needs one controlled source of truth before implementation
  expands across four parallel workstreams.
- **Owner:** Person 4/repository steward.
- **Status:** Locked by the project owner on 2026-08-24.

### D-011 — Versioned contracts coordinate parallel work

- **Decision:** Parallel owners integrate through versioned contracts and
  Person 4-owned mocks/replay fixtures. Shared changes are proposal-first and
  require Person 4 plus every affected owner before implementation/merge.
- **Why:** This prevents one owner from silently breaking another owner while
  still allowing independent development.
- **Source:** Controlling four-person assignment.

### D-012 — Progress is durable and merge-enforced

- **Decision:** Every implementation pull request updates its owner status,
  adds a work-item record, and updates the changelog and affected authoritative
  docs in the same change. CI checks these companions from the diff.
- **Why:** Agent context must be reconstructed from the repository without
  relying on chat history or manual recollection.
- **Trade-off:** Contributors must resolve documentation conflicts before merge.

### D-013 — Keep the single `kyra` package layout

- **Decision:** Keep one distributable package rooted at `src/kyra`. Future
  modules live under `kyra` or appropriate `kyra/<area>/` subpackages; the
  assignment-named top-level packages such as `src/data` and `src/geometry`
  are not created. Existing `kyra.*` public imports remain stable.
- **Why:** The implemented modules, package discovery configuration, and
  architecture already use the `kyra` package. Keeping that layout avoids
  unnecessary import migration while preserving clear owner subpackages.
- **Owner:** Person 4.
- **Approved:** 2026-08-26.

## Pending decisions

### P-003 — Public distribution licence confirmation

`pyproject.toml` declares `AGPL-3.0-only` and the repository now contains the matching full licence text. The compatibility review for datasets, 3D assets, and optional model dependencies is still outstanding.

### P-004 — T4 execution owner

The assignment requires target T4 validation. Record who provides the environment, who runs the frozen commands, and where the test report is stored.

### P-005 — Manifest object metadata

Person 4 approved the version 1.1 proposal on 2026-08-26, including the
object-mask path, shape-family field and four proposed shape-family values. The
approved policy keeps version 1.0 readable, writes version 1.1, uses a
manifest-specific `MANIFEST_SCHEMA_VERSION = "1.1"` with supported versions
`{"1.0", "1.1"}`, rejects unsupported versions, and leaves the shared runtime
`SCHEMA_VERSION` unchanged. Person 2 and Person 3 each confirmed on 2026-08-30:
"Not affected — confirmed that the proposed P-005 manifest changes do not
require changes to their runtime/consumer contracts. Proceed." The exact
proposal and approval checklist are in `docs/P1-02_CONTRACT_CHANGE_PROPOSAL.md`.

The approved manifest extension is now implemented as C-006. The current code
supports both manifest versions 1.0 and 1.1, writes version 1.1, keeps the
runtime contract unchanged, adds `FrameRecord.object_mask_path`, adds
`GroundTruthEvent.shape_family`, and exposes `ScenarioFrameSource.object_mask`.
The repository still does not implement downstream geometry or tracking logic;
those owners remain separately scoped and unchanged.

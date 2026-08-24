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

## Pending decisions

### P-001 — Final package layout

The assignment names `src/data`, `src/simulation`, `src/calibration`, and `src/baseline`, while the current repository uses `src/kyra/*.py`. Person 4 must confirm whether the team will keep one package or create top-level packages. The implementation plan assumes one `kyra` package to minimize disruption.

### P-002 — Git hosting and release links

This folder is not connected to Git. The team must decide the repository host, default branch, review process, and release owner before changelog comparison links or CI instructions can be finalized.

### P-003 — Public distribution licence confirmation

`pyproject.toml` declares `AGPL-3.0-only` and the repository now contains the matching full licence text. The compatibility review for datasets, 3D assets, and optional model dependencies is still outstanding.

### P-004 — T4 execution owner

The assignment requires target T4 validation. Record who provides the environment, who runs the frozen commands, and where the test report is stored.

### P-005 — Manifest object metadata

Person 4 must approve the version 1.1 proposal for an object-mask path and shape
family before those fields are added to the shared manifest. The exact proposal,
compatibility rules, and approval checklist are in
`docs/P1-02_CONTRACT_CHANGE_PROPOSAL.md`.

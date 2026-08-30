# Gate 1 Evidence — Contract Compatibility

## Scope

This gate covers the shared contract-compatibility layer only. It proves the repository’s frozen schema and compatibility contract surfaces are correctly defined and usable through the deterministic Person 4 mock layer. It does not claim real Person 1/2/3 algorithm completion, end-to-end processing, or Gate 5 success.

## Gate definition

See [../INTEGRATION_GATES.md](../INTEGRATION_GATES.md). The exit criteria require frozen versions for the core shared contract surfaces, compatibility tests for units/coordinates/timestamps/invalid values, and executable mocks/fixtures for the producer and consumer surfaces. The final requirement is that real owner implementations remain outside the gate proof and must not be mistaken for mock compatibility completion.

## Contract surfaces and evidence

### FramePacket
- Contract: `src/kyra/contracts.py::FramePacket`
- Freeze/approval: C-001, foundation implemented
- Evidence: `tests/test_contracts.py` checks type normalization, invalid depth handling, and invalid shape rejection
- Real implementation status: Person 1 owns the real production path; no real Person 1 implementation is claimed by this gate proof

### BaselineArtifact
- Contract: `src/kyra/contracts.py::BaselineArtifact`
- Freeze/approval: C-002, foundation implemented
- Evidence: `tests/test_contracts.py` checks runtime normalization and mismatched image arrays
- Real implementation status: Person 1 owns the real production path; no real Person 1 implementation is claimed by this gate proof

### VolumeChangeEvent
- Contract: `src/kyra/contracts.py::VolumeChangeEvent`
- Freeze/approval: C-003, type foundation only; producer absent
- Evidence: compatibility fixture and mock geometry in `tests/test_person4_adapters.py` and `tests/test_pipeline.py`
- Real implementation status: Person 2 owns the production implementation; not available yet

### PersonTrack
- Contract: `src/kyra/contracts.py::PersonTrack`
- Freeze/approval: C-004, type foundation only; producer absent
- Evidence: compatibility fixture and mock tracking in `tests/test_person4_adapters.py`
- Real implementation status: Person 3 owns the production implementation; not available yet

### AlertEvent
- Contract: `src/kyra/contracts.py::AlertEvent`
- Freeze/approval: C-005, type foundation only; producer absent
- Evidence: compatibility fixture and mock rule evaluation in `tests/test_person4_adapters.py` and `tests/test_pipeline.py`
- Real implementation status: Person 3 owns the production implementation; not available yet

### ScenarioManifest
- Contract: `src/kyra/manifest.py::ScenarioManifest`
- Freeze/approval: C-006, implemented and approved as manifest 1.1 while `SCHEMA_VERSION` remains 1.0
- Evidence: `tests/test_manifest.py` checks schema validation, version compatibility, and manifest behavior
- Real implementation status: Person 1 owns the data-side production path; no real Person 1 implementation is claimed by this gate proof

### ShelfConfig / C-007 boundary
- Contract: `src/kyra/contracts.py::ShelfConfig`, `src/kyra/manifest.py::ShelfConfigRecord`
- Freeze/approval: C-007 approved and frozen with the exact five-field boundary: `shelf_id`, `roi_xyxy`, `bounds_min_m`, `bounds_max_m`, `voxel_size_m`
- Evidence: `tests/test_contracts.py` verifies the exact five-field boundary and runtime/persisted equivalence
- Real implementation status: Person 4 owns the shared configuration boundary; Person 1/2/3 consumers use it, but no owner algorithm is claimed here

## Deterministic Person 4 mock proof

The repository’s Person 4 mocks and bounded pipeline demonstrate the contract-compatible behavior required by Gate 1 without claiming that real P1/P2/P3 algorithms exist.

### Implemented and evidenced
- `src/kyra/adapters.py`
- `src/kyra/pipeline.py`
- `tests/test_person4_adapters.py`
- `tests/test_pipeline.py`

These tests verify:
- mock baseline creation and valid output
- mock tracking output and event compatibility
- mock geometry output and volume-change compatibility
- mock rule evaluation and alert output
- queue size 2 behavior with oldest-unprocessed-frame dropping
- timestamp-based 2-second temporal confirmation
- evidence-frame propagation

## Real owner status

This gate only proves contract compatibility and deterministic mock compatibility. It does not prove:
- Person 1 baseline generation is complete
- Person 2 geometry/change logic is complete
- Person 3 tracking/rules logic is complete
- Gate 5 end-to-end pipeline completeness

Those remain separate responsibilities and downstream gates.

## Verification

The following commands were run successfully on 2026-08-30:

- `D:\Projects\kyra-shelf-guard\.venv\Scripts\python.exe -m pytest -q` — 83 passed
- `D:\Projects\kyra-shelf-guard\.venv\Scripts\python.exe -m ruff check .` — passed
- `D:\Projects\kyra-shelf-guard\.venv\Scripts\python.exe -m compileall -q src tests scripts` — passed
- `D:\Projects\kyra-shelf-guard\.venv\Scripts\python.exe scripts/check_repo_consistency.py` — passed

## Gate decision

Gate 1 is complete for the shared contract compatibility layer based on the repository’s existing frozen contracts, compatibility tests, and deterministic Person 4 mock evidence. Real Person 1/2/3 implementation work remains required for Gates 2–5 and beyond.

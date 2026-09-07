# Person 4 Status — Integration and Evaluation

- **Status:** Complete
- **Last updated:** 2026-09-07

## Implemented

- Foundation shared Python contracts and scenario schema exist.
- Repository charter, ownership, contract/change control, per-owner status, work-item records, integration gates, agent instructions, GitHub templates, CI, and governance validation are established.
- Private GitHub repository `DontHash/kyra-shelf-guard` is configured and Core CI has passed on Python 3.11 and 3.12.
- P-001 was approved: the repository retains one distributable `kyra` package, future modules remain under `kyra` or its area subpackages, and existing `kyra.*` imports are preserved.
- C-001 `FramePacket` compatibility fixture and focused tests cover identity, timestamp ordering, array shapes and dtypes, metric depth values, camera coordinates, and invalid-depth handling without changing the production contract.
- C-002 `BaselineArtifact` compatibility fixture and focused tests cover runtime array normalization, shapes, portable-component values, metadata, checksum state, and complete NPZ/JSON round trips without changing the production contract.
- C-003 `VolumeChangeEvent` compatibility fixture and focused tests cover event fields, shelf-frame geometry, timestamps, quality values, and default metadata without changing the production contract.
- C-004 `PersonTrack` compatibility fixture and focused tests cover field preservation, pose-keypoint normalization, near-shelf timestamp behavior, and invalid keypoint shapes without changing the production contract.
- C-005 `AlertEvent` compatibility fixture and focused tests cover field preservation, evidence-frame defaults, and frozen-instance behavior without changing the production contract.
- C-006 manifest implementation is complete: `ScenarioManifest` supports manifest versions 1.0 and 1.1, `FrameRecord.object_mask_path`, `GroundTruthEvent.shape_family`, and the new `ScenarioFrameSource.object_mask(frame_id)` access path without changing the runtime `SCHEMA_VERSION` or `FramePacket` contract.
- C-007 v1 is approved and frozen as the exact shelf boundary `shelf_id`, `roi_xyxy`, `bounds_min_m`, `bounds_max_m`, and `voxel_size_m` using the existing `ShelfConfig` and `ScenarioManifest.shelf` models; no second `RuntimeConfig` or parallel schema was introduced.
- Deterministic Person 4 mock providers and a bounded mock pipeline were implemented and validated, covering mock compatibility for baseline, tracking, geometry, alert evaluation, queue behavior, temporal confirmation, and evidence propagation.
- Issue #10 adds separate plain-English teammate documentation and an agent-facing technical route without changing runtime contracts or product evidence.
- The documentation hub now maps audience paths, authority by purpose, and the durable status/work-item/contract/gate folders without moving authoritative files.
- The collaboration guide now defines the repository's normal branch, verified
  commit, and push commands, with direct routes for agents and teammates.

## Active

Gate 1 contract compatibility is complete for the shared compatibility layer. Person 4 mock, adapter, and pipeline work is complete and validated. Real Person 1, Person 2, and Person 3 algorithm work is not being claimed as complete; downstream Gates 2–5 remain dependent on real owner outputs and end-to-end validation.

WI-010 (audience-specific documentation split) and the documentation
reconciliation issues #15 and #18 are merged and closed.

## Issue #15 — stale shared test-count summaries

Resolved on 2026-09-06: shared summaries no longer present everlasting
"current" test totals. The decision is dated totals plus evidence pointers:
`README.md`, `docs/people/README.md`, and `docs/PROJECT_STATUS.md` now carry
"161 tests … 2026-09-06" wording, `docs/TESTING.md` documents the dated-total
rule, and the G2 gate row reflects the merged Person 1 work. A stale count
must not be restated as a current total.

## Issue #53 — dependency pins synchronized with Dependabot bumps

Resolved on 2026-09-07: `pyproject.toml`, `requirements.lock`, and
`requirements-gpu.lock` synchronized with Dependabot bumps #47/#48/#49
(pydantic 2.13.5 core; torch 2.14.0 and ultralytics 8.4.138 optional
tracking/midas). 189 tests passed with the synced core lock installed,
including the byte-identical golden-pack regeneration audit. The dependency
refresh logs in `docs/DEVELOPMENT.md`/`docs/TESTING.md` record the true
validated pin run; the three Dependabot PRs were closed as superseded by
work-item `docs/work-items/WI-053-integrate-dependency-bumps.md`.

## Issue #36 — dependency lock synchronization

Resolved on 2026-09-06: `requirements.lock` pins synchronized with the merged
pyproject pins (numpy 2.4.6, opencv-python-headless 5.0.0.93, pydantic
2.13.4); 161 tests passed with the synced lock installed, including the
byte-identical golden-pack regeneration audit under OpenCV 5. The dependency
refresh log in `docs/DEVELOPMENT.md`/`docs/TESTING.md` now reflects the true
validated pin run.

## Issue #18 — change-impact ownership alignment

Implemented and merged on 2026-09-06 as `0b034c0` (PR #29): the
change-impact classifier now classifies the named Person 1 generation,
conversion, and verification scripts (`generate_golden_pack.py`,
`convert_ocid.py`, `verify_person1.py`) and the Person 1 test names (`golden`,
`midas`, `provenance`) as Person 1, excluding them from the governance
requirement. All other `scripts/` and `.github/` changes remain Person 4
governance. Focused governance tests were added in
`tests/test_repo_governance.py`, and `CONTRIBUTING.md` documents the rule.
This unblocked and merged PRs #27 (golden pack, `327a905`) and #28 (verify
script, `7f2fd84`).

## Gate 1 closure

The repository evidence satisfies the Gate 1 exit criteria for the shared contract-compatibility layer. This covers the frozen contract definitions, the compatibility tests, and the deterministic Person 4 mock coverage. It does not claim that Person 1, Person 2, or Person 3 have completed real algorithm implementations.

The frozen contract and mock/evidence layer is complete; downstream Gates 2–5 remain blocked by real owner implementations and end-to-end validation, not by a missing contract or mock layer.

## Next

- Complete downstream Gate 2 baseline and data work with Person 1.
- Complete downstream Gate 3 geometry work with Person 2.
- Complete downstream Gate 4 tracking and rule work with Person 3.
- Complete Gate 5 end-to-end validation after the real owner outputs are integrated.

## Blocked or pending

- Person 1–4 GitHub handles are not assigned; `@DontHash` is temporary steward/CODEOWNER.
- Server-enforced branch protection is unavailable for this private repository on the current GitHub plan.
- Gates 2–5 remain blocked by real Person 1/2/3 algorithm outputs and end-to-end chain validation.
- Contract mocks, pipeline, evaluation, T4 validation, and release process remain separate from the frozen contract compatibility proof and must not be mistaken for real owner algorithm completion.

## Evidence

- `docs/gates/GATE-1.md` records the contract compatibility evidence for the frozen shared surfaces.
- Compatibility and mock proof: `tests/test_contracts.py`, `tests/test_manifest.py`, `tests/test_person4_adapters.py`, and `tests/test_pipeline.py`.
- Current verification on 2026-08-30: `python -m pytest -q` — 83 passed.
- Current verification on 2026-08-30: `python -m ruff check .` — passed.
- Current verification on 2026-08-30: `python -m compileall -q src tests scripts` — passed.
- Current verification on 2026-08-30: `python scripts/check_repo_consistency.py` — passed.
- Work item `../work-items/WI-010-audience-documentation.md` tracks the audience-specific documentation route.
- WI-010 verification on 2026-09-01: 83 tests passed; Ruff, compileall,
  repository consistency, change-impact, and diff checks passed on Python 3.12.7.

# Person 4 Status — Integration and Evaluation

- **Status:** In progress
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

Gate 1 contract compatibility remains complete. WI-077 provided the reviewed
Gate 5 synthetic vertical slice through the real Person 1 baseline/frame source,
Person 2 geometry provider, Person 3 replay/proximity/rules, and Person 4
orchestration. Gate 5 is now closed for this deterministic scenario scope.

The critical blocking regression (Issue #79 - Camera Drift) has been resolved
by Person 2. The multi-frame `camera-drift` scenario correctly evaluates with
zero events and zero alerts. Gate 5 is closed for the reviewed synthetic slice;
public-data validation, live tracking, Gate 6 evaluation, and Gate 7 release
validation remain open.

WI-081 (Video Demo Command) added a `kyra demo` CLI subcommand and a `kyra.viz`
annotation module to generate end-to-end MP4 inference videos.

WI-010 (audience-specific documentation split) and the documentation
reconciliation issues #15 and #18 are merged and closed.

## Issue #72 — additive change to `src/kyra/adapters.py`

On 2026-09-09 the Person 3 lazy tracking adapter integration added
`LazyUltralyticsTrackingProvider` to the Person 4-owned `src/kyra/adapters.py`
as a purely additive class plus one `__all__` entry (no protocol or mock
change, no contract impact), coordinated under P4 review per the ownership
matrix. Recorded here so the shared surface's history stays attributable.

## Issue #69 — Person 3 Gate 4 evidence and change-impact classifier update

On 2026-09-09 the Person 3 Gate 4 evidence integration (see
`docs/gates/GATE-4.md`) extended `scripts/check_change_impact.py` with
`PERSON3_SCRIPTS = frozenset({"generate_person3_gate4_evidence.py"})`,
following the WI-018 (Person 1) and WI-067 (Person 2) precedents, with a
companion governance test and updated `CONTRIBUTING.md`. Gate 4 status
remains a Person 4 decision after review of the evidence record.

## WI-067 — Person 2 Gate 3 evidence and change-impact classifier update

Updated `scripts/check_change_impact.py` on 2026-09-07 to recognize
`PERSON2_SCRIPTS = frozenset({"verify_person2.py"})`, classifying Person 2's
verification runner under Person 2 and excluding it from Person 4 governance
requirements, following the precedent established for `PERSON1_SCRIPTS` in
WI-018. Added companion test to `tests/test_repo_governance.py` and updated
`CONTRIBUTING.md`. Person 2 submitted formal Gate 3 evidence record
`docs/gates/GATE-3.md` for Person 4 review.

## Issue #15 — stale shared test-count summaries

Resolved on 2026-09-06: shared summaries no longer present everlasting
"current" test totals. The decision is dated totals plus evidence pointers:
`README.md`, `docs/people/README.md`, and `docs/PROJECT_STATUS.md` now carry
"161 tests … 2026-09-06" wording, `docs/TESTING.md` documents the dated-total
rule, and the G2 gate row reflects the merged Person 1 work. A stale count
must not be restated as a current total.

## Issue #56 — Phase 0 decisions completed (P-003, G0.4)

Resolved on 2026-09-07 with project-owner approval: P-003 (OCID CC-BY 4.0
research use and tiny-example publication with attribution, recorded as
D-014) and P-004/G0.4 (target-T4 runner assigned to the Kaggle free-T4 GPU
notebook, recorded as D-015 with runner notebook
`notebooks/kyra_t4_validation.ipynb`). `data-sources/provenance.json` now
records `licence_review_status: approved-2026-09-07 (D-014)` while
`status: pending_download` stays honest. The only remaining Phase 0 item is
the independent Person 1 handoff sign-off (issue #57).

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

The frozen contract and mock/evidence layer is complete, and the reviewed
synthetic vertical slice is closed by Gate 5. Public-data validation, live
tracking, frozen evaluation, and release validation remain open; none is
blocked by a missing contract or mock layer.

## Next

- Define and freeze the Gate 6 evaluation split and reporting requirements.
- Gather the remaining public-data and live-tracking evidence before Gate 7.

## Blocked or pending

- Person 1–4 GitHub handles are not assigned; `@DontHash` is temporary steward/CODEOWNER.
- Server-enforced branch protection is unavailable for this private repository on the current GitHub plan.
- Contract mocks, pipeline, evaluation, T4 validation, and release process remain separate from the frozen contract compatibility proof and must not be mistaken for real owner algorithm completion.

## Evidence

- `docs/gates/GATE-1.md` records the contract compatibility evidence for the frozen shared surfaces.
- Compatibility and mock proof: `tests/test_contracts.py`, `tests/test_manifest.py`, `tests/test_person4_adapters.py`, and `tests/test_pipeline.py`.
- Current verification on 2026-08-30: `python -m pytest -q` — 83 passed.
- Current verification on 2026-08-30: `python -m ruff check .` — passed.
- Current verification on 2026-08-30: `python -m compileall -q src tests scripts` — passed.
- Current verification on 2026-08-30: `python scripts/check_repo_consistency.py` — passed.
- WI-077 focused verification on 2026-09-07:
  `python -m pytest -q tests/test_vertical_pipeline.py` — 13 passed.
- WI-077 visual-review verification on 2026-09-07:
  `python -m pytest -q tests/test_simulator.py tests/test_vertical_pipeline.py`
  — 16 passed; the browser-loaded default case matched one expected removal and
  one expected alert across 37 replay frames.
- WI-077 branch regression verification on Windows/Python 3.12.7 on 2026-09-07:
  full suite — 215 passed; Ruff, byte-compilation, repository consistency, and
  change-impact validation passed.
- WI-077 five-command smoke on Windows/Python 3.12.7: one synthetic removal,
  one linked alert, evaluation passed, five-run benchmark p50 28.1047 ms.
- Camera-drift negative evidence: evaluation exited 1 with expected no change
  but actual `REMOVAL`; zero alert events; tracked as #79.
- Work item `../work-items/WI-010-audience-documentation.md` tracks the audience-specific documentation route.
- WI-010 verification on 2026-09-01: 83 tests passed; Ruff, compileall,
  repository consistency, change-impact, and diff checks passed on Python 3.12.7.

# Changelog

All notable changes to this project will be documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). Version numbers will follow [Semantic Versioning](https://semver.org/spec/v2.0.0.html) once releases begin.

## [Unreleased]

- Person 2 single acceptance verifier runner (`scripts/verify_person2.py`) executing
  all Gate 3 acceptance checks across golden pack G01–G10 replay, known-volume accuracy,
  failure-path assertions, serialization determinism, and real-sensor OCID sequence evaluation (exit code 0).
- Person 2 automated Gate 3 test suite (`tests/test_geometry_gate3.py`) asserting
  G01–G10 invariants, volume $\le 10\%$ error threshold, failure mode suppression,
  and deterministic `VolumeChangeEvent` hashing.
- Formal Integration Gate 3 evidence record (`docs/gates/GATE-3.md`) documenting all
  replay metrics, volume accuracy tables, failure-mode behavior, and real-sensor trials.
- Change-impact classifier support for Person 2 verification scripts (`PERSON2_SCRIPTS`)
  in `scripts/check_change_impact.py`, companion test in `tests/test_repo_governance.py`,
  and documentation in `CONTRIBUTING.md`.
- Person 2 formal specification (`docs/PERSON2_SPEC.md`) and phased implementation
  plan (`docs/PERSON2_IMPLEMENTATION_PLAN.md`) grounded in research literature for
  retail on-shelf availability, M3C2 error propagation ($3\sigma$), and TSDF occlusion safety.
- Person 2 shelf-only registration, 3D unprojection/projection utilities, and
  camera drift compensation module (`src/kyra/geometry/registration.py` and
  `src/kyra/geometry/points.py`) with drift envelope checks and residual threshold rejection.
- Person 2 signed depth differencing (`src/kyra/differencing/signed_diff.py`) with
  per-pixel adaptive $3\sigma$ noise thresholding and safe unknown-depth handling.
- Person 2 occlusion safety and shelf visibility monitoring (`src/kyra/occlusion/safety.py`)
  with automatic confirmation suppression below 70% visibility.
- Person 2 3D connected-component clustering (`src/kyra/geometry/clustering.py`) and
  ray frustum metric volume estimation (`src/kyra/geometry/volume.py`).
- Person 2 sliding-window temporal persistence tracker and baseline restocking hooks
  (`src/kyra/geometry/temporal_state.py`).
- Person 2 production `ShelfGeometryProvider` (`src/kyra/geometry/provider.py`) implementing
  the shared `GeometryProvider` protocol with sub-2 ms p95 processing latency.
- Person 1 lightweight deterministic RGB-D scenario generation with seeded
  object placement, all four approved shape families, lossless manifest 1.1
  assets, and offline same-seed byte/hash stability checks.
- Person 1 candidate golden scenario pack with ten deterministic, replayable
  synthetic behaviors, portable manifests, a reviewed seed/shape matrix,
  checksum inventory, and byte-identical regeneration checks. The pack remains
  explicitly unfrozen pending the D-009 team confirmation.
- Person 1 OCID conversion mapping (`src/kyra/ocid.py`) with strict metadata
  parsing, millimetre depth mapping that keeps zero depth unknown, valid and
  object masks, windowed addition/removal event derivation, addition-to-removal
  reversal with re-created monotonic timestamps, last-seen object-mask
  semantics on removal frames, and a SHA-256 source gate, all replayed through
  the manifest 1.1 reader on a tiny committed OCID fixture.
- Person 1 provenance record and schema (`data-sources/provenance.json`,
  `data-sources/README.md`) covering licence, checksum, selection, exclusion,
  conversion, attribution, and environment-neutral path rules with honest
  pending-download status.
- Person 1 OCID conversion CLI entry point (`scripts/convert_ocid.py`):
  discovery, SHA-256 source gate, and `--reverse` addition-to-removal
  conversion around the merged `kyra.ocid` mapping, verified against the mini
  fixture and replayed through `ScenarioFrameSource`.
- Person 1 single verification entry point (`scripts/verify_person1.py`):
  schema, golden-checksum (with line-ending-canonical hashing so Windows CRLF
  and T4 LF trees verify identically), reader replay, baseline build, MiDaS
  policy, and provenance checks, collecting all failures with clear messages
  and exiting 0 only when every Person 1 acceptance check passes offline. It
  fails loudly with an explicit message when the golden pack or provenance
  record is absent rather than passing vacuously.
- Separate docs/people/ plain-English guides and a docs/agents/ technical
  routing page so teammates and coding agents have distinct starting paths.
- Add a documentation hub that maps audience routes, technical authority, and
  status/work-item/contract/gate folders without breaking stable paths.
- Add one authoritative, command-level routine for safely creating or
  synchronizing an issue branch, reviewing and staging a coherent diff,
  committing it, and pushing it without rewriting shared history.
- Private-repository collaboration foundation with a four-owner charter, path
  boundaries, contract registry and approval process, integration gates,
  per-owner status files, work-item and handoff templates, and AI-agent preflight.
- GitHub issue and pull-request templates, CODEOWNERS, Dependabot, core CI, and
  change-impact governance checks.
- Repository consistency validation for required control documents, status
  records, and relative documentation links.
- Person 4 C-001 FramePacket compatibility fixture and focused contract tests.
- Person 4 C-002 BaselineArtifact compatibility fixture and focused persistence tests.
- Person 4 C-004 PersonTrack compatibility fixture and focused contract tests.
- Person 4 C-005 AlertEvent compatibility fixture and focused contract tests.
- Person 4 C-003 VolumeChangeEvent compatibility fixture and focused contract tests.
- P1-01 foundation tests for shared contracts, strict manifests, RGB-D replay,
  baseline build/save/load, and MiDaS anchor alignment.
- P1-02 shared-manifest change proposal covering object masks, shape families,
  backward compatibility, ownership, and approval gates.
- Approved P-005/C-006 manifest extension implementing versioned object metadata,
  `FrameRecord.object_mask_path`, `GroundTruthEvent.shape_family`, supported
  manifest versions 1.0 and 1.1, object-mask reader validation, and the
  `ScenarioFrameSource.object_mask(frame_id)` API without changing the runtime
  `FramePacket` contract or shared `SCHEMA_VERSION`.
- Replay access to saved per-frame track annotations without exposing mutable
  manifest state.
- Person 3 replay tracking, shelf proximity, occlusion masking, deterministic
  removal-alert association, edge-case tests, and integration tests.
- Person 1 baseline calibration hardening tests: mixed-resolution and
  changed-intrinsics frame batches reject, unsafe occupancy-grid dimensions
  reject, an empty shelf is entirely fixed geometry, injected per-pixel jitter
  raises the noise sigma above the 1 mm floor, and the calibration checksum is
  stable across repetitions, sensitive to median-affecting changes, and
  documented as absorbing single-frame outlier pixels.
- Person 1 known-volume acceptance suite with box, cylinder, and irregular
  union shapes at varied positions (0.55-1.72 litres, 0.94-0.97 m tops on a
  1.0 m plane) all within the 10% volume limit, plus a hanging-plate guard
  case that records the expected void-column overestimate for Person 2's
  occlusion-safe geometry scope.
- Person 1 MiDaS policy tests: MIDAS_ALIGNED frames label artifacts
  approximate, the flag survives save/load round trips, negative and NaN
  relative inverses stay unknown in aligned output, and the residual limit is
  explicit and enforceable.
- Human-facing project README and documentation map.
- Person 1 specification, implementation plan, system requirements, architecture, data, development, testing, and decision documents.
- Repository instructions for coding agents in `AGENTS.md`.
- Project capability map in `SKILLS.md`.
- LLM-friendly documentation index in `llms.txt`.
- Contribution and documentation maintenance rules.
- Full AGPL-3.0-only licence text matching the package metadata.

### Fixed

- Manifest write checksums now describe the exact bytes saved to disk.
- RGB, valid-depth-mask, and occlusion-mask size mismatches now fail with clear errors.
- Scenario asset paths can no longer escape the scenario folder.
- Person 3 replay now represents absent pose annotations as an empty `(0, 3)`
  keypoint array instead of failing while constructing `PersonTrack`.

### Changed

- The repository README now leads with a short, honest project explanation and
  routes readers by audience instead of presenting the full governance map first.
- Documentation policy and repository validation now preserve the people/agent
  split and require affected summaries to follow authoritative technical truth.
- Correct P-005 links and registry wording so the approved design is clearly
  distinguished from its still-pending implementation.
- GitHub workflow actions now use current immutable release commits instead of deprecated Node 20 action versions.
- Security-patched pins for Wheel 0.46.2, Setuptools 83.0.0, pytest 9.0.3,
  and optional Torch 2.13.0 in response to the first GitHub dependency scan.
- Dependency pins synchronized with Dependabot bumps #47/#48/#49 (issue #53):
  pydantic 2.13.4 -> 2.13.5 (core), torch 2.13.0 -> 2.14.0 (optional
  tracking/midas), ultralytics 8.4.123 -> 8.4.138 (optional tracking);
  `requirements.lock` and `requirements-gpu.lock` updated to match, and the
  full 189-test suite passes with the synced core lock installed, including
  the byte-identical golden-pack regeneration audit.
- Phase 0 decisions completed (issue #56): P-003 resolved as D-014 (OCID
  CC-BY 4.0 research use approved for tiny example publication with
  attribution), G0.4 resolved as D-015 (target-T4 runner = Kaggle free-T4
  GPU notebook via `notebooks/kyra_t4_validation.ipynb`); OCID licence state
in `data-sources/provenance.json` updated while `pending_download` stays
   honest.
- Target-T4 leg executed on 2026-09-07 on the Kaggle free-T4 GPU notebook
  (issue #64): dated report `docs/PERSON1_TEST_REPORT_T4_2026-09-07.md` —
  189 tests passed in 1.95s, seven-check verifier exit 0, golden-pack
  regeneration audit byte-identical (116/116), optional GPU published-pin
  smoke probe exit 0, on the frozen `main` `65d3707` snapshot; independent
  handoff sign-off remains open (issue #59).

### Known gaps

- No release tag exists; release ownership and frozen release evidence begin at
  Integration Gate 7.
- GitHub handles for Persons 1–4 still need to be recorded in the team roster;
  `@DontHash` is the temporary repository steward and CODEOWNER.
- Server-enforced branch protection for the private repository requires a GitHub
  plan upgrade; CI and review policy are present but not platform-enforced.
- The change-impact classifier now recognizes the named Person 1
  generation/conversion/verification scripts and the Person 1 test names
  (`golden`, `midas`, `provenance`) instead of classifying them as Person 4
  governance, with focused classifier tests and an updated governing rule in
  `CONTRIBUTING.md`.
- Shared project summaries now use dated test totals with evidence pointers
  instead of everlasting "current" totals, so a stale number cannot be
  restated as current truth (issue #15).
- Project-level workstream and per-person summaries align with the current
  owner status files: Person 3 shows its merged tracking/rules work and Person
  4 its completed shared layer, and the testing guide's "Current truth" block
  states the dated 161-test total (issue #34).
- `requirements.lock` synchronized with the merged dependency pins (numpy
  2.4.6, opencv-python-headless 5.0.0.93, pydantic 2.13.4); the full 161-test
  suite passes with the synced lock installed, including the byte-identical
  golden-pack regeneration audit under OpenCV 5 (issue #36).
- Person 1 handoff package (`docs/PERSON1_HANDOFF.md`): reproducible install,
  playbook, recorded 2026-09-06 outputs, limitations, and an independent
  sign-off block, with the remaining completion decisions (D-009, P-003,
  G0.4) consolidated under issue #40.
- The golden scenario pack is frozen: `golden-pack.json` records
  `pack_status: frozen` and `decision_status: D-009-confirmed-2026-09-06` after
  the scenario-ten confirmation (D-009), with the regeneration inventory and
  audit updated accordingly.
- OCID licence research recorded for P-003 (CC-BY 4.0 on the official TU Wien
  Research Data record; published archive md5 `aa0eff01…`), the provenance
  record completed with the researched fields, and the G0.4 target-T4
  assignment proposal recorded with its exact command set and report path
  (issue #44). Research only — download still requires team confirmation.
- The deterministic scenario generator is implemented and merged; the golden
  scenario pack remains a candidate awaiting team confirmation of D-009 and
  the change-impact alignment in issue #18 (now resolved by PR #29).
  `scripts/convert_ocid.py` and `scripts/verify_person1.py` are unblocked by
  that classifier fix; the OCID archive itself has not been downloaded. The
  CLI remains unimplemented. The candidate pack's audit test uses a
  line-ending-canonical inventory comparison so a Windows checkout under
  `core.autocrlf=true` verifies identically.

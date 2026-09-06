# Changelog

All notable changes to this project will be documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). Version numbers will follow [Semantic Versioning](https://semver.org/spec/v2.0.0.html) once releases begin.

## [Unreleased]

### Added

- Person 1 lightweight deterministic RGB-D scenario generation with seeded
  object placement, all four approved shape families, lossless manifest 1.1
  assets, and offline same-seed byte/hash stability checks.
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

### Known gaps

- No release tag exists; release ownership and frozen release evidence begin at
  Integration Gate 7.
- GitHub handles for Persons 1–4 still need to be recorded in the team roster;
  `@DontHash` is the temporary repository steward and CODEOWNER.
- Server-enforced branch protection for the private repository requires a GitHub
  plan upgrade; CI and review policy are present but not platform-enforced.
- The deterministic scenario generator is implemented and merged; the golden
  scenario pack remains a candidate awaiting team confirmation of D-009 and
  the change-impact alignment in issue #18. `scripts/convert_ocid.py` is
  implemented locally but joins the push with that classifier fix; the OCID
  archive itself has not been downloaded. The verification script and CLI
  remain unimplemented.

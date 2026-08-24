# Changelog

All notable changes to this project will be documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). Version numbers will follow [Semantic Versioning](https://semver.org/spec/v2.0.0.html) once releases begin.

## [Unreleased]

### Added

- Private-repository collaboration foundation with a four-owner charter, path
  boundaries, contract registry and approval process, integration gates,
  per-owner status files, work-item and handoff templates, and AI-agent preflight.
- GitHub issue and pull-request templates, CODEOWNERS, Dependabot, core CI, and
  change-impact governance checks.
- Repository consistency validation for required control documents, status
  records, and relative documentation links.
- P1-01 foundation tests for shared contracts, strict manifests, RGB-D replay,
  baseline build/save/load, and MiDaS anchor alignment.
- P1-02 shared-manifest change proposal covering object masks, shape families,
  backward compatibility, ownership, and approval gates.
- Replay access to saved per-frame track annotations without exposing mutable
  manifest state.
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

### Changed

- GitHub workflow actions now use current immutable release commits instead of deprecated Node 20 action versions.

### Known gaps

- No release tag exists; release ownership and frozen release evidence begin at
  Integration Gate 7.
- GitHub handles for Persons 1–4 still need to be recorded in the team roster;
  `@DontHash` is the temporary repository steward and CODEOWNER.
- Server-enforced branch protection for the private repository requires a GitHub
  plan upgrade; CI and review policy are present but not platform-enforced.
- The deterministic generator, golden scenario pack, OCID converter, and CLI remain unimplemented.
- Manifest version 1.1 object-mask and shape-family fields remain pending Person
  4 approval.

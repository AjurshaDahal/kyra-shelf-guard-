# Project Charter

## Mission

Build a reproducible RGB-D research prototype that detects persistent suspicious shelf removals without SKU-specific or theft-scenario training. The system must separate metric geometry evidence from person tracking and policy, then integrate those independent outputs through versioned contracts.

## System claim

Kyra may report a **suspicious shelf-removal alert** when persistent missing shelf volume remains after visibility/occlusion checks and a non-authorized person track was near the affected shelf region during the configured prior time window. The assignment's current rule window is two seconds.

Kyra does not prove theft, infer intent, identify a legal offender, or replace human review. Documentation, user interfaces, evaluation reports, and papers must preserve that boundary.

## Product boundaries

### In scope

- Replayable RGB-D scenario input and deterministic synthetic fixtures.
- Metric shelf calibration, baselines, registration, signed change, 3D clustering, and volume estimation.
- Replay tracks plus optional pretrained person tracking.
- Occlusion and unknown-depth safety.
- Authorization/proximity policy and deterministic alert output.
- One bounded pipeline, five planned CLI commands, frozen evaluation, comparison reporting, and reproducible evidence.

### Out of scope unless the assignment is formally changed

- SKU classification or per-product training.
- Face recognition, identity inference, or intent classification.
- A claim that an alert is proof of theft.
- Training a central theft detector.
- Production surveillance deployment, payment/POS integration, or autonomous enforcement.
- Committing bulk datasets, weights, point clouds, generated runs, or private footage.

## Operating principles

1. **Contracts before coupling.** Owners exchange versioned data objects, never private implementation assumptions.
2. **One accountable owner.** Every module, work item, status update, and gate has one owner even when reviewers collaborate.
3. **Proposal before shared change.** No consumer changes a public contract to make local work easier.
4. **Offline deterministic core.** Core tests do not require credentials, network, CUDA, Blender, downloads, or live cameras.
5. **Evidence is scoped.** A unit result proves only the tested unit; synthetic results remain labelled synthetic.
6. **Documentation changes with truth.** Code, contracts, status, decisions, and evidence land together.
7. **Unknown means unknown.** Missing/invalid depth and occluded regions do not count as free shelf space.

## Source of truth

The controlling assignment is authoritative. Approved decisions and contract-change records specialize it. Specifications and contract registries define expected interfaces. Tests describe verified implemented behavior. Plans and status files coordinate work but cannot silently override higher sources.

See [Documentation Policy](DOCUMENTATION_POLICY.md) for conflict handling.

## Project definition of done

The project is complete only when:

- all four owner packages pass their independent acceptance checks;
- all seven [Integration Gates](INTEGRATION_GATES.md) pass against the same frozen schemas and configuration;
- a clean supported environment can run the five planned CLI commands;
- the ten-scenario golden pack is byte-stable and loads on Windows and the target T4 environment;
- frozen evaluation outputs and comparison metrics are reproducible from recorded commands;
- licence/provenance records cover every external dataset, asset, and model;
- the paper/report uses honest claim language and distinguishes synthetic, public-data, and end-to-end evidence;
- release notes, tag, reviewed commit, and remote repository state agree.

No plan, green build, open port, package version, or partial pipeline run substitutes for these conditions.

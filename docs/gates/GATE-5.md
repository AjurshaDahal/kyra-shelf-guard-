# Gate 5 Evidence — Vertical Scenario Pipeline

- **Gate:** Gate 5 (Vertical Integration)
- **Accountable owner:** Person 4 (Integration and Evaluation)
- **Reviewers:** Person 1 (baseline/frames), Person 2 (geometry), Person 3 (tracking/rules)
- **Date recorded:** 2026-09-07
- **Status:** Approved / Closed

## Scope

This gate covers the full vertical integration of the system. It proves that the Person 1 input sources, Person 2 geometry provider, Person 3 proximity/rules engine, and Person 4 pipeline orchestrator all successfully interact according to their defined `kyra.contracts`. 

It also provides proof of end-to-end execution on deterministic synthetic scenarios and includes an end-to-end video visualizer (`kyra demo`).

## Gate definition

Per `docs/INTEGRATION_GATES.md`:
> **Exit:** E2E vertical slice working. The orchestration pipeline calls real algorithms from P1, P2, and P3, producing proper serialized evidence.

## Verification environment

- **Operating System:** Windows 11
- **Python version:** Python 3.12.7
- **Dependencies:** requirements.lock (synchronized)

## Evidence Record

### 1. Test Suite Coverage & Regression
The entire suite of 216 integration and unit tests passes cleanly. This includes multi-frame end-to-end scenarios running through the real `run_scenario` pipeline. The Issue #79 camera drift regression was verified to pass correctly without generating false removals.

### 2. End-to-End Visual Demo (WI-081)
The `kyra demo` subcommand was run on the `suspicious-removal` and `occlusion-then-removal` profiles. It successfully intercepted frame-by-frame depth candidate masks, tracked bounding boxes, and alert status, synthesizing an annotated `demo.mp4` video.

### 3. Change-Impact & Consistency
The repository consistency and change-impact scripts passed successfully, validating governance and module boundaries.


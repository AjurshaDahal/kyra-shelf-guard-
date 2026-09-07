# Gate 4 Evidence — Deterministic Tracking, Proximity, and Alert Rules

- **Gate:** Gate 4 (Tracking and rules)
- **Accountable owner:** Person 3 (Tracking, Proximity, and Alert Logic)
- **Reviewers:** Person 4 (rules contract and gate decision), Person 2 (occlusion-mask input), Person 1 (replay input)
- **Date recorded:** 2026-09-09
- **Status:** Evidence compiled; awaiting Person 4 gate decision

## Scope

This record covers the deterministic Person 3 layer named in the Gate 4 exit
criteria: deterministic replay tracking, frame-aligned person masks, shelf
proximity, authorization suppression, the two-second association window, the
deterministic alert/no-alert matrix, and serialized `PersonTrack`/`AlertEvent`
evidence. It does **not** claim Gate 4 closure; live/upstream integration-level
items are listed as limitations.

## Gate definition

Per [docs/INTEGRATION_GATES.md](../INTEGRATION_GATES.md): deterministic replay
tracking; lazy optional pretrained adapter; frame-aligned masks; shelf
proximity; authorization suppression; two-second association window;
deterministic alert/no-alert matrix; serialized `PersonTrack`/`AlertEvent`
evidence.

## Verification environment (merged main, 2026-09-09)

- **Operating System:** Windows, Python 3.12.7 (frozen `requirements.lock` pins)
- **Runtime schema:** `1.0`; **manifest:** `1.1`; **rule version:** `P3-001`
- **Determinism:** pure CPU, offline; reproducible generator committed

## Evidence generator

`scripts/generate_person3_gate4_evidence.py` (integrated via pull request
#71): builds a deterministic synthetic scenario (4x5 frames, explicit
invalid-depth/mask/occlusion pixels), replays it through `ReplayTracker`,
`update_proximity`, and `evaluate_removal_alert`, asserts every expected
outcome, and writes serialized evidence plus `SHA256SUMS.txt`.

### Deterministic alert/no-alert matrix

| Case | Expected | Actual | Alert ID |
|---|---|---|---|
| `eligible-removal` | alert | alert | `alert-matrix-case-track-7` |
| `authorized-person` | no alert | no alert | — |
| `restock-mode` | no alert | no alert | — |
| `below-minimum-volume` | no alert | no alert | — |
| `outside-two-second-window` | no alert | no alert | — |
| `addition-direction` | no alert | no alert | — |

Association window `2000000000 ns`; proximity threshold `1.0 m`; minimum
alert volume `5e-05 m^3`; all assertions passed on two independent runs with
identical generated manifests.

### Serialized evidence SHA-256 (generated 2026-09-09, frozen environment)

| File | SHA-256 |
|---|---|
| `person3-alert-001.json` | `0e404f95cf4138ccc0f40d9e9bfee4091629444912dc82a097b7cd33aa93dcf0` |
| `person3-gate4-matrix.json` | `4c321e7411df005c07100369df420fee99c6169289219fb6815bf4cc117ea704` |
| `person3-track-001.json` | `fa720b05cb30fa0e4a2e344389733e278fcac440fa7fba11f1634c8a32fef29d` |
| `scenario/scenario.json` | `f090758c032815611a9a445ba9a7f62d337d792c2151f8fa7b56f5c435778b06` |
| `scenario/depth/frame-0001.png` | `d3eb95af99059da55f40705a8e5cea83872064b0f67abce2e1cecab1a407d080` |
| `scenario/depth/frame-0002.png` | `6bba066f5e1f325d4651aaeb6440dd533d7a6bd3c53171992be26eb6609beb2c` |
| `scenario/rgb/frame-0001.png` | `96377d1d397dab2b32d4b1cda5d6a14ce8b318cf21a8d23048bbadd2f3cc9abe` |
| `scenario/rgb/frame-0002.png` | `9ff7893b6099c5e1ba4b69b753259ec82dd964952414e2eec1117b85ae65f725` |
| masks (valid/occlusion, x2) | `185d685c…`, `4c6cabcde…`, `88c9c74c…`, `ff31c4490…` |

The commit-time `SHA256SUMS.txt` covers all twelve files; regeneration on the
merged tree produced byte-identical hashes.

### Deterministic replay artifact

Track ID `7`, near shelf `True`, last near timestamp `2000000000 ns`; alert
`alert-p3-g4-removal-001-track-7` under rule `P3-001`. Replay tracks with
absent pose keypoints normalize to the empty `(0, 3)` pose array (regression
covered by the merged suite).

## Acceptance commands and exit codes (merged tree, 2026-09-09)

| Check | Command | Exit | Result |
|---|---|---|---|
| Evidence generator | `python scripts/generate_person3_gate4_evidence.py` | 0 | matrix asserted; manifest written |
| Full repository suite | `python -m pytest -q` | 0 | 195 passed |
| Lint | `python -m ruff check .` | 0 | passed |
| Compilation | `python -m compileall -q src tests scripts` | 0 | passed |
| Consistency | `python scripts/check_repo_consistency.py` | 0 | passed |
| Change impact | `python scripts/check_change_impact.py --base origin/main` | 0 | passed (companions) |

## Limitations and open items

- The matrix consumes **synthetic** `VolumeChangeEvent` inputs (frozen C-003);
  the real Person 2 -> Person 3 chain is validated at Gate 5.
- The lazy optional pretrained detector/tracker adapter is not implemented;
  it is optional for the deterministic core per D-002 and remains a
  Gate-4-review decision point for Person 4.
- Person masks are bounding-box-based (not instance segmentation); recorded
  as a limitation per Person 3 risk notes.
- Generated evidence lives under `evidence/` (git-ignored by design); the
  committed generator reproduces it deterministically.
- This record is an evidence compilation; Person 4 decides gate status in
  `docs/PROJECT_STATUS.md` with the linked record.

## Conclusion

The deterministic Gate 4 exit-criteria evidence (replay tracking, masks,
proximity, authorization, window, matrix, serialized evidence) is compiled and
reproducible on the merged tree. Gate 4 is **pending Person 4 review and
decision**; the integration-level chain items are tracked for Gate 5.
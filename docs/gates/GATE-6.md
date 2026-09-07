# Gate 6 Evidence — Frozen Evaluation

- **Gate:** Gate 6 (Frozen Evaluation)
- **Accountable owner:** Person 4 (Integration and Evaluation)
- **Status:** Prepared; not closed
- **Scope:** Synthetic deterministic end-to-end evaluation only
- **Contracts:** C-001 through C-007 unchanged; C-008 not created

## Prepared evaluation split

The P4 evaluator and prepared split are under review at:

- `src/kyra/evaluation/gate6.py`
- `scenario-fixtures/gate6/gate6.json`
- `scenario-fixtures/gate6/checksums.sha256`
- `scripts/generate_gate6_split.py`

The split contains the approved ten scenario categories. Each manifest has 30
baseline frames, at least seven event-observation frames, 100 ms frame spacing,
synthetic evidence labeling, and `frozen_test` split labeling. The existing
G01-G10 golden fixtures remain unchanged and continue to serve as regression
fixtures rather than the full Gate 6 scoring split.

## Evaluation output

The evaluator consumes existing `ScenarioManifest` ground truth and
`run_scenario` output. It reports per scenario and aggregate:

- event and alert TP/FP/FN;
- event TP requires the predicted change type to match the expected change type;
  event presence is reported separately;
- precision, recall, and F1;
- event and alert confusion matrices;
- event timing differences where one expected and one actual event exist;
- volume relative error and 3D bounds IoU where applicable;
- baseline checksum and event-frame traceability;
- explicitly excluded track-association, live-tracker, public-OCID, and
  real-world-calibration metrics.

For the current ten-scenario validation scope it also reports geometry balanced
accuracy, missing-volume recall, median absolute percentage volume error,
current-scope theft-rule recall and false-positive rate, Wilson 95% binomial
intervals, and latency availability. The theft-rule and false-positive metrics
are explicitly marked `unavailable_final_dataset` because Section 10 requires
120 positive and 300 negative trials.

Run the prepared evaluation with:

```powershell
.\.venv\Scripts\python.exe -m kyra.cli evaluate --split scenario-fixtures\gate6
```

Current report evidence was generated on the Windows Python 3.12.10 working
tree based on source commit `9f4d65302841c0621788c7a6ae8a907d3b26997e`:

- report: `evidence/gate6-evaluation.json`
- report SHA-256: `9acf402768d274cc871b7aaf5fd712256879096e094e1429cf62c8e7b846a343`
- dependency lock SHA-256: `1331d0b0eb691152ef44c5723087b22ae27f4c0a854c4969957661e065c0cd1a`
- fixture inventory SHA-256: `d0d94170a757793a63a49ba9ed6f30508ea7333b2108034d51b32867e5d04c7e`

Acceptance thresholds are not embedded in the evaluator. Optional timing,
volume, and bounds thresholds must be supplied explicitly. The evaluator
distinguishes no thresholds configured, partially configured thresholds, all
thresholds passed, all thresholds failed, and thresholds that cannot be
evaluated because no applicable metric exists. No numeric Gate 6 threshold is
approved by this record.

## Reproducibility

The split records generator version, seeds, exact frame configuration, manifest
paths, expected event types, expected alert decisions, and a SHA-256 inventory.
The evaluator validates the inventory and cross-validates index metadata against
each manifest before running. Its serialized output uses the stable split ID,
not a machine-specific absolute path. The reviewed commit,
Python environment, dependency-lock checksum, approved thresholds, exact
command, output report, and report checksum remain required for Gate 6 closure.

## Section 10 final acceptance boundary

The current split is deterministic synthetic vertical validation, not the
Section 10 final evaluation dataset. Full acceptance remains pending:

- 120 frozen positive removal scenarios;
- 300 frozen negative controls;
- 60 BlenderProc scenarios across 20 held-out categories;
- 60 reversed OCID transitions;
- final 111-of-120 theft-rule recall and at-most-3-of-300 false-alert checks;
- final confidence intervals and category-level generalization evidence;
- IDF1/HOTA only if suitable annotated tracking data becomes available.

The current report does not claim any of these final criteria are passed.

Current ten-scenario validation results are reported separately from final
acceptance: geometry balanced accuracy `1.0` (4/4 removal, 6/6 non-removal),
missing-volume recall `1.0` (4/4 event proxy), median applicable volume error
`123.31547582373172%`, theft-rule recall `1.0` on 2/2 current positive controls,
and false-positive rate `0.0` on 0/8 current negative controls. The latter two
are not Section 10 acceptance results because the required 120/300 trials are
absent. Stage latency is unavailable; complete-pipeline timing remains
available through the existing `kyra benchmark` command.

## Limitations and open approval

- This is synthetic/replay evidence only.
- Public OCID accuracy is not evaluated.
- Live tracker accuracy is not evaluated.
- Track-association accuracy is excluded because the approved ground truth does
  not contain associated track IDs.
- Real-world calibration is not evaluated.
- No comparison baseline is defined by the repository or this preparation.
- The prepared fixture contents and numeric Gate 6 acceptance thresholds still
  require project-owner approval.
- Gate 6 is not closed by this scaffolding.

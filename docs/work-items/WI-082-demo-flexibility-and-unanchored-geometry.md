# WI-082: Demo Flexibility and Unanchored Geometry Handling

**Owner:** Person 2, Person 4
**Status:** Complete
**Date:** 2026-09-08

## Scope

1. Fix UTF-8 encoding regression in docs/gates/GATE-5.md introduced in commit c5694bf (non-UTF-8 CP1252 byte \x97 breaking repository consistency checks).
2. Clean up .gitignore encoding and ignore patterns for generated demo videos, temporary scenarios, and OCID working directories.
3. Enhance kyra demo CLI subcommand in src/kyra/cli.py to accept existing scenario directories (containing scenario.json) or scenario manifest files directly, while preserving example scenario generation when a case name is given.
4. Refine ShelfGeometryProvider in src/kyra/geometry/provider.py:
   - When a dataset lacks fixed shelf structure (insufficient_fixed_geometry_points, as in uncalibrated tabletop recordings like OCID), gracefully fall back to raw depth rather than aborting the stream.
   - Maintain strict rejection when fixed geometry is present and either the camera drift envelope or registration residual threshold is exceeded.
   - Compare dominant cluster volume (
_vol >= a_vol) when both removal and addition candidate pixels are present, avoiding false change classifications.
5. Add unit test coverage in 	ests/test_demo.py for running kyra demo on an existing scenario.

## Accomplished

- Restored UTF-8 compliance in docs/gates/GATE-5.md; scripts/check_repo_consistency.py and 	ests/test_repo_governance.py pass cleanly.
- Updated src/kyra/geometry/provider.py with physical registration fallback and volume comparison.
- Extended src/kyra/cli.py _demo and verified with 	ests/test_demo.py.
- Full repository test suite passes (217/217).

## Evidence

- 	ests/test_demo.py passes (2/2).
- Full test suite: 217/217 passed.
- 
uff check . passed.
- check_repo_consistency.py passed.

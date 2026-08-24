# Project Skills and Ownership

This is a project capability map, not a list of packages to install. It explains what Person 1 must be able to do, what is delivered to the team, and how each skill is proven.

| Skill | In simple words | Main output | Proof |
|---|---|---|---|
| RGB-D input handling | Read colour and distance images safely | Valid `FramePacket` sequence | Valid and malformed scenario tests |
| Deterministic simulation | Create repeatable shelf situations | Scenario generator and golden pack | Same seed produces identical output |
| Camera and shelf calibration | Describe where the camera and shelf are | Intrinsics, transform, and shelf bounds | Validation tests and known synthetic scene |
| Baseline building | Build the opening model of the shelf | Saved `BaselineArtifact` | 30-frame fusion and reload test |
| Depth-noise handling | Know when sensor differences are unreliable | Per-pixel noise estimate and valid mask | Noisy/invalid-depth tests |
| Fixed-versus-portable separation | Keep shelf structure separate from items | Fixed mask and portable components | Structure and under-0.5 m³ tests |
| Metric-depth fallback | Convert MiDaS output only when anchors make it trustworthy | Approximate aligned depth | Good-anchor and rejection tests |
| Dataset conversion | Put OCID scenes into Kyra’s common format | Converted scenarios | Fixture conversion and schema validation |
| Data provenance | Record where data came from and its rules | Provenance manifest | URL, checksum, licence, selection, exclusion review |
| Cross-platform verification | Show the same fixtures work in both environments | Windows and T4 test reports | Recorded commands, versions, and results |

## Supporting knowledge

Person 1 should be comfortable with:

- NumPy arrays and units.
- OpenCV image reading and lossless PNG files.
- Basic camera intrinsics and 3D coordinate transforms.
- Pydantic validation.
- Pytest fixtures and parameterized tests.
- File hashing with SHA-256.
- Dataset licence and attribution records.

Open3D, BlenderProc, Torch, and MiDaS are optional or extended-path skills. The core golden pack must not require them to run.

## Team handoff skills

Person 1 must also communicate the following clearly:

- What each scenario is expected to do.
- Which frames form the opening baseline.
- Which depth pixels are unknown.
- Which shelf parts are fixed and which objects are portable.
- Whether depth is measured or only approximately aligned.
- Which dataset records were accepted or excluded and why.

See the [Person 1 Specification](docs/PERSON1_SPEC.md) for the formal requirements and the [Implementation Plan](docs/PERSON1_IMPLEMENTATION_PLAN.md) for the build order.

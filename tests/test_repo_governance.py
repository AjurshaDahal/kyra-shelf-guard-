from pathlib import Path

from scripts.check_change_impact import assess_changes
from scripts.check_repo_consistency import validate_repository

ROOT = Path(__file__).resolve().parents[1]


def test_repository_control_documents_are_consistent() -> None:
    assert validate_repository(ROOT) == []


def test_product_change_requires_owner_status_work_item_and_changelog() -> None:
    errors = assess_changes({"src/kyra/geometry/volume.py"})

    assert "PERSON2 changes require docs/status/PERSON2.md" in errors
    assert "implementation/governance changes require CHANGELOG.md" in errors
    assert any("docs/work-items" in error for error in errors)


def test_owner_change_with_required_companions_passes() -> None:
    changed = {
        "src/kyra/tracking/replay.py",
        "docs/status/PERSON3.md",
        "docs/work-items/WI-12-replay-tracks.md",
        "CHANGELOG.md",
    }

    assert assess_changes(changed) == []


def test_shared_contract_change_requires_approval_record_and_registry() -> None:
    changed = {
        "src/kyra/contracts.py",
        "docs/status/PERSON4.md",
        "docs/work-items/WI-20-contract.md",
        "CHANGELOG.md",
    }

    errors = assess_changes(changed)

    assert "shared-contract changes require docs/CONTRACTS.md" in errors
    assert "shared-contract changes require docs/DECISIONS.md" in errors
    assert any("contract-changes" in error for error in errors)


def test_person1_named_scripts_do_not_require_person4_governance() -> None:
    for script in ("generate_golden_pack.py", "convert_ocid.py", "verify_person1.py"):
        changed = {
            f"scripts/{script}",
            "docs/status/PERSON1.md",
            "docs/work-items/WI-18-p1-script.md",
            "CHANGELOG.md",
        }

        assert assess_changes(changed) == []


def test_person2_named_scripts_classify_as_person2_and_exclude_governance() -> None:
    for script in ("verify_person2.py",):
        changed = {
            f"scripts/{script}",
            "docs/status/PERSON2.md",
            "docs/work-items/WI-067-gate3-geometry-evidence.md",
            "CHANGELOG.md",
        }

        assert assess_changes(changed) == []


def test_person3_named_scripts_classify_as_person3_and_exclude_governance() -> None:
    for script in ("generate_person3_gate4_evidence.py",):
        changed = {
            f"scripts/{script}",
            "docs/status/PERSON3.md",
            "docs/work-items/WI-069-gate4-evidence.md",
            "CHANGELOG.md",
        }

        assert assess_changes(changed) == []


def test_other_scripts_still_require_person4_and_governance_docs() -> None:
    changed = {"scripts/ci_governance_tool.py", "CHANGELOG.md"}

    errors = assess_changes(changed)

    assert "PERSON4 changes require docs/status/PERSON4.md" in errors
    assert "governance changes require AGENTS.md or CONTRIBUTING.md" in errors


def test_person1_named_test_files_classify_as_person1() -> None:
    for test_path in (
        "tests/test_golden_pack.py",
        "tests/test_midas_alignment.py",
        "tests/test_provenance.py",
    ):
        changed = {
            test_path,
            "docs/status/PERSON1.md",
            "docs/work-items/WI-18-p1-test.md",
            "CHANGELOG.md",
        }

        assert assess_changes(changed) == []

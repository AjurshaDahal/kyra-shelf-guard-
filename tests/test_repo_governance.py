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

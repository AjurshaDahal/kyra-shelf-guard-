import json
from pathlib import Path

from kyra.cli import main


def test_demo_command_creates_video(tmp_path: Path, capsys) -> None:
    scenario_dir = tmp_path / "demo-scenario"
    video_path = tmp_path / "custom_demo.mp4"

    assert (
        main(
            ["demo", str(scenario_dir), "--case", "suspicious-removal", "--video", str(video_path)]
        )
        == 0
    )

    output = json.loads(capsys.readouterr().out)
    assert output["command"] == "demo"
    assert output["frames_processed"] > 0
    assert output["events_detected"] > 0
    assert output["alerts_triggered"] > 0

    assert video_path.exists()
    assert video_path.stat().st_size > 0

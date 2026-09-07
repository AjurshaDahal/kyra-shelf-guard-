import builtins

import numpy as np
import pytest

from kyra.adapters import LazyUltralyticsTrackingProvider


def test_lazy_tracking_provider_does_not_import_ultralytics(monkeypatch):
    imported = []

    original_import = builtins.__import__

    def tracking_import(name, *args, **kwargs):
        if name == "ultralytics" or name.startswith("ultralytics."):
            imported.append(name)
            raise AssertionError("Ultralytics was imported during adapter construction")
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", tracking_import)

    provider = LazyUltralyticsTrackingProvider()

    assert provider._model is None
    assert imported == []


def test_lazy_tracking_provider_reports_missing_optional_dependency(monkeypatch):
    provider = LazyUltralyticsTrackingProvider()

    original_import = builtins.__import__

    def missing_import(name, *args, **kwargs):
        if name == "ultralytics":
            raise ImportError("simulated missing ultralytics")
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", missing_import)

    with pytest.raises(RuntimeError, match="Optional pretrained tracking"):
        provider._load_model()


def test_lazy_tracking_provider_converts_model_results(shelf_config, make_frame_packet):
    provider = LazyUltralyticsTrackingProvider()

    class FakeTensor:
        def __init__(self, value):
            self.value = np.asarray(value)

        def cpu(self):
            return self

        def numpy(self):
            return self.value

    class FakeBoxes:
        xyxy = FakeTensor([[1.0, 2.0, 10.0, 12.0]])
        id = FakeTensor([7])

    class FakeResult:
        boxes = FakeBoxes()

    class FakeModel:
        def track(self, **kwargs):
            assert kwargs["persist"] is True
            assert kwargs["classes"] == [0]
            assert kwargs["tracker"] == "bytetrack.yaml"
            assert kwargs["verbose"] is False
            return [FakeResult()]

    provider._model = FakeModel()

    frame_packet = make_frame_packet()
    tracks = provider.track([frame_packet], shelf_config)

    assert len(tracks) == 1
    assert tracks[0].track_id == 7
    assert tracks[0].timestamp_ns == frame_packet.timestamp_ns
    assert tracks[0].box_xyxy == (1.0, 2.0, 10.0, 12.0)
    assert tracks[0].pose_keypoints_xyc.shape == (0, 3)
    assert tracks[0].position_m is None
    assert tracks[0].near_shelf is False

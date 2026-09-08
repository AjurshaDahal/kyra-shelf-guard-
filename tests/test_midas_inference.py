"""Optional pinned MiDaS v3.1 inference adapter tests."""

from __future__ import annotations

from contextlib import nullcontext
from types import SimpleNamespace

import numpy as np
import pytest

from kyra.baseline import LazyMidasV31DepthEstimator


class _FakeBatch:
    def __init__(self) -> None:
        self.device: str | None = None

    def to(self, device: str) -> _FakeBatch:
        self.device = device
        return self


class _FakeOutput:
    def __init__(self, values: np.ndarray) -> None:
        self.values = values

    def detach(self) -> _FakeOutput:
        return self

    def cpu(self) -> _FakeOutput:
        return self

    def numpy(self) -> np.ndarray:
        return self.values


class _FakeModel:
    def __init__(self, values: np.ndarray) -> None:
        self.values = values
        self.device: str | None = None
        self.evaluating = False

    def to(self, device: str) -> _FakeModel:
        self.device = device
        return self

    def eval(self) -> _FakeModel:
        self.evaluating = True
        return self

    def __call__(self, batch: _FakeBatch) -> _FakeOutput:
        assert batch.device == self.device
        return _FakeOutput(self.values)


def _fake_torch(values: np.ndarray) -> tuple[SimpleNamespace, _FakeModel, list[str]]:
    model = _FakeModel(values)
    entries: list[str] = []

    def load(repository: str, entry: str, *, trust_repo: bool) -> object:
        assert repository == LazyMidasV31DepthEstimator.REPOSITORY
        assert trust_repo is True
        entries.append(entry)
        if entry == "transforms":
            return SimpleNamespace(swin256_transform=lambda _image: _FakeBatch())
        assert entry == "DPT_SwinV2_T_256"
        return model

    torch = SimpleNamespace(
        cuda=SimpleNamespace(is_available=lambda: False),
        hub=SimpleNamespace(load=load),
        no_grad=nullcontext,
    )
    return torch, model, entries


def test_midas_adapter_is_lazy_and_returns_resized_float32(monkeypatch: pytest.MonkeyPatch) -> None:
    torch, model, entries = _fake_torch(
        np.array([[[1.0, 2.0, 3.0], [1.5, 2.5, 3.5]]], dtype=np.float32)
    )
    monkeypatch.setattr("kyra.baseline.importlib.import_module", lambda name: torch)
    estimator = LazyMidasV31DepthEstimator()

    assert not estimator.loaded
    relative = estimator.predict(np.zeros((4, 6, 3), dtype=np.uint8))

    assert estimator.loaded
    assert estimator.device == "cpu"
    assert model.evaluating
    assert entries == ["transforms", "DPT_SwinV2_T_256"]
    assert relative.shape == (4, 6)
    assert relative.dtype == np.float32
    assert np.all(np.isfinite(relative))


def test_midas_adapter_rejects_invalid_input_before_loading() -> None:
    estimator = LazyMidasV31DepthEstimator()

    with pytest.raises(ValueError, match="HxWx3"):
        estimator.predict(np.zeros((4, 6), dtype=np.uint8))
    with pytest.raises(ValueError, match="uint8"):
        estimator.predict(np.zeros((4, 6, 3), dtype=np.float32))

    assert not estimator.loaded


def test_midas_adapter_rejects_unavailable_cuda(monkeypatch: pytest.MonkeyPatch) -> None:
    torch, _, _ = _fake_torch(np.ones((1, 2, 2), dtype=np.float32))
    monkeypatch.setattr("kyra.baseline.importlib.import_module", lambda name: torch)

    with pytest.raises(RuntimeError, match="unavailable"):
        LazyMidasV31DepthEstimator(device="cuda").predict(
            np.zeros((2, 2, 3), dtype=np.uint8)
        )


def test_midas_adapter_rejects_nonfinite_model_output(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    torch, _, _ = _fake_torch(
        np.array([[[1.0, np.nan], [2.0, 3.0]]], dtype=np.float32)
    )
    monkeypatch.setattr("kyra.baseline.importlib.import_module", lambda name: torch)

    with pytest.raises(RuntimeError, match="non-finite"):
        LazyMidasV31DepthEstimator().predict(np.zeros((2, 2, 3), dtype=np.uint8))

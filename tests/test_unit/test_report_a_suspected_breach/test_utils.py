import builtins

from report_a_suspected_breach.utils import get_active_regimes


def test_get_active_regimes_normal():
    regimes = get_active_regimes()
    assert isinstance(regimes, list)
    assert all(isinstance(regime, dict) for regime in regimes)
    assert len(regimes) >= 1


def test_get_active_regimes_import_error(monkeypatch):
    def mock_import(*args, **kwargs):
        raise ImportError

    monkeypatch.setattr(builtins, "__import__", mock_import)
    regimes = get_active_regimes()
    assert isinstance(regimes, list)
    assert len(regimes) == 0
    assert regimes == []

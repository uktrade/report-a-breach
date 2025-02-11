import builtins
from builtins import __import__ as builtin_import

from report_a_suspected_breach.utils import get_active_regimes


def test_get_active_regimes_normal():
    regimes = get_active_regimes()
    assert isinstance(regimes, list)
    assert all(isinstance(regime, dict) for regime in regimes)
    assert len(regimes) >= 1


def test_get_active_regimes_import_error(monkeypatch):
    def mock_import(*args, **kwargs):
        if args[3][0] == "active_regimes":
            raise ImportError
        else:
            # we need to provide some route to the original import as the teardown of the test will fail otherwise
            return builtin_import(*args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", mock_import)
    regimes = get_active_regimes()
    assert isinstance(regimes, list)
    assert len(regimes) == 0
    assert regimes == []

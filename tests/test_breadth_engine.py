import pandas as pd
from core.breadth_engine import BreadthEngine


def _make_df(values):
    dates = pd.date_range("2024-01-01", periods=len(values), freq="D")
    return pd.DataFrame({"close": values}, index=dates)


def test_engine_true_when_threshold_met():
    df1 = _make_df(range(60))
    df2 = _make_df(range(60))
    engine = BreadthEngine(ma_days=50, threshold=0.5)
    assert engine.evaluate({"A": df1, "B": df2}) is True


def test_engine_false_when_threshold_not_met():
    df1 = _make_df(range(60))
    df2 = _make_df([1] * 60)
    engine = BreadthEngine(ma_days=50, threshold=0.75)
    assert engine.evaluate({"A": df1, "B": df2}) is False


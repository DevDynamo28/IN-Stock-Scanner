import pandas as pd
import numpy as np

from core.rs_calculator import compute_rs_alpha, add_ama, add_donchian_channel


def test_compute_rs_alpha_basic():
    dates = pd.date_range("2020-01-01", periods=30, freq="D")
    stock_close = pd.Series(np.arange(100, 130), index=dates)
    index_close = pd.Series(np.arange(200, 230), index=dates)
    stock_df = pd.DataFrame({"close": stock_close})
    index_df = pd.DataFrame({"close": index_close})

    expected = (stock_close / stock_close.shift(21) - 1) - (index_close / index_close.shift(21) - 1)
    result = compute_rs_alpha(stock_df, index_df, period=21)
    pd.testing.assert_series_equal(result, expected)


def test_add_ama_full_length():
    df = pd.DataFrame({"close": np.arange(1, 21)})
    result = add_ama(df.copy(), period=10)
    expected = df["close"].ewm(span=10, adjust=False).mean()
    pd.testing.assert_series_equal(result["ama"], expected)


def test_add_ama_short_df():
    df = pd.DataFrame({"close": np.arange(5)})
    result = add_ama(df.copy(), period=10)
    assert result["ama"].isna().all()


def test_add_donchian_channel_full_length():
    lookback = 20
    data = {
        "close": np.arange(1, 26),
        "high": np.arange(1, 26),
        "low": np.arange(1, 26) - 2,
    }
    df = pd.DataFrame(data)
    result = add_donchian_channel(df.copy(), lookback=lookback)

    expected_high = df["high"].rolling(window=lookback).max()
    expected_low = df["low"].rolling(window=lookback).min()
    expected_breakout = (df["close"] > expected_high.shift(1)).astype(int)

    pd.testing.assert_series_equal(result["donchian_high"], expected_high)
    pd.testing.assert_series_equal(result["donchian_low"], expected_low)
    pd.testing.assert_series_equal(result["donchian_breakout"], expected_breakout)


def test_add_donchian_channel_short_df():
    df = pd.DataFrame({"close": np.arange(5), "high": np.arange(5), "low": np.arange(5)})
    result = add_donchian_channel(df.copy(), lookback=20)
    assert (result["donchian_breakout"] == 0).all()
    assert result["donchian_high"].isna().all()
    assert result["donchian_low"].isna().all()

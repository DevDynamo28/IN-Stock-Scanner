import types
from datetime import date

import data.live_fetch.kite_client as kite_client


class DummyKite:
    def __init__(self, *args, **kwargs):
        pass

    def set_access_token(self, token):
        pass

    def historical_data(self, instrument_token, from_date, to_date, interval="day"):
        return [
            {"date": "2024-01-01", "open": 1, "high": 2, "low": 0.5, "close": 1.5},
            {"date": "2024-01-02", "open": 1.5, "high": 2.5, "low": 1, "close": 2},
        ]

    def instruments(self):
        return []


class DummyDF:
    def __init__(self, data):
        self.data = data
        self.columns = list(data[0].keys()) if data else []
        self.index = None

    def __getitem__(self, key):
        return [row[key] for row in self.data]

    def __setitem__(self, key, values):
        if not isinstance(values, list):
            values = [values] * len(self.data)
        for row, val in zip(self.data, values):
            row[key] = val
        if key not in self.columns:
            self.columns.append(key)

    def set_index(self, key, inplace=True):
        self.index = [row[key] for row in self.data]
        if not inplace:
            return self

    @property
    def empty(self):
        return not self.data


class DummyPandas(types.SimpleNamespace):
    def __init__(self):
        super().__init__(DataFrame=DummyDF, to_datetime=lambda x: x)


def test_fetch_historical_ohlc(monkeypatch):
    monkeypatch.setattr(kite_client, "KiteConnect", DummyKite)
    monkeypatch.setattr(kite_client.ZerodhaKiteClient, "build_token_cache", lambda self: {"RELIANCE": 738561})
    monkeypatch.setattr(kite_client, "pd", DummyPandas())

    client = kite_client.ZerodhaKiteClient(api_key="key", api_secret="secret", access_token="token")
    df = client.fetch_historical_ohlc("RELIANCE", date(2024, 1, 1), date(2024, 1, 2))

    assert isinstance(df, DummyDF)
    assert df.data[0]["close"] == 1.5
    assert df.index == ["2024-01-01", "2024-01-02"]

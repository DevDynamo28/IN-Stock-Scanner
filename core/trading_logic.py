from strategy.rs_entry_engine import run_daily_entry_engine


def generate_signals(api_key, api_secret, access_token):
    """Run existing RS entry engine and return signals."""
    df = run_daily_entry_engine(api_key, api_secret, access_token)
    signals = []
    for _, row in df.iterrows():
        signals.append({
            "symbol": row["symbol"],
            "action": "buy",
            "qty": 1,
        })
    return signals

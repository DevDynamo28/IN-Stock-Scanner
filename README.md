# IN-Stock-Scanner


IN-Stock-Scanner is a collection of utilities and trading scripts for scanning NSE stocks using the Zerodha Kite API. It focuses on relative strength (RS) calculations, sector analysis and basic backtesting utilities. The project can run a daily scanner with live data and also provides a simple backtest runner.
## Quick start

Install dependencies and then run:

```bash
python main.py            # runs the daily scanner
python backtest_runner.py # runs the basic backtest
```


## Folder layout

```
config/         # YAML configuration files and secrets
core/           # RS, breadth and sector analysis utilities
data/           # Live data fetch helpers built on Kite API
account/       # Paper trading account logic
broker/        # Zerodha wrapper with live/paper modes
dashboard/     # Streamlit dashboard for monitoring
strategy/       # Entry/exit engines and models
output/         # Telegram helper and generated trade reports
notebooks/      # Jupyter notebooks for research
tools/          # Small helper utilities (charting, etc.)
main.py         # Runs the daily scanner with live data
backtest_runner.py  # Simple historical backtester
gen_token.py        # Utility to generate and save Kite access tokens
```

## Installation

Python 3.11 or newer is required. Install dependencies with `pip`:

```bash
pip install -r requirements.txt
```

A minimal `pyproject.toml` is included. If you prefer using it, run:

```bash
pip install .
```

## Generating Kite access tokens

First add your API credentials to `config/secrets.yaml` (copy
`secrets.example.yaml` if the file doesn't exist) under the keys
`kite_api_key` and `kite_api_secret`. The `gen_token.py` helper reads these
values automatically, so there's no need to modify the script. Then run:

```bash
python gen_token.py
```

The script prints a login URL. Open the URL in a browser, authenticate with Zerodha and copy the `request_token` from the redirect URL. Paste it back into the script when prompted. A new `access_token` will be generated and stored back into `config/secrets.yaml`.

## Running the live scanner

After installing dependencies and generating tokens, launch the daily scanner:

```bash
python main.py
```

The script reads `config/params.yaml` for the stock list and other parameters, fetches recent OHLC data from Kite and prints any RS entry candidates. Trade reports are saved under `output/reports` and alerts are sent via Telegram if credentials are configured.

## Running the backtest

`backtest_runner.py` performs a simple walk‑forward test over a date range.
Adjust the `start_date` and `end_date` variables at the top of the file and run:

```bash
python backtest_runner.py
```

Results are written to `output/backtest_trades.csv`.
This project scans stocks using Zerodha Kite data and generates reports.

## Configuration

Sensitive credentials are loaded from `config/secrets.yaml` which is ignored by
Git. An example template is provided at `config/secrets.example.yaml`.

Create your own secrets file by copying the example and filling in the values:

```bash
cp config/secrets.example.yaml config/secrets.yaml
# edit config/secrets.yaml with your tokens
```

If a `secrets.yaml` file is not present, the application will fall back to
environment variables (`KITE_API_KEY`, `KITE_API_SECRET`, `KITE_ACCESS_TOKEN`,
`TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`) or the example file.


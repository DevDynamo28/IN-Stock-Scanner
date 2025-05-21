# IN-Stock-Scanner

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

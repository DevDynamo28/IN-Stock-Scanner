import os
import yaml


ENV_VARS = {
    'kite_api_key': 'KITE_API_KEY',
    'kite_api_secret': 'KITE_API_SECRET',
    'kite_access_token': 'KITE_ACCESS_TOKEN',
    'telegram_bot_token': 'TELEGRAM_BOT_TOKEN',
    'telegram_chat_id': 'TELEGRAM_CHAT_ID',
}


def _load_from_env():
    data = {}
    for key, env_key in ENV_VARS.items():
        value = os.getenv(env_key)
        if value is None:
            continue
        if key == 'telegram_chat_id' and ',' in value:
            data[key] = [v.strip() for v in value.split(',')]
        else:
            data[key] = value
    return data


def load_secrets(path='config/secrets.yaml'):
    """Load secrets from a YAML file, falling back to env vars or the example."""
    secrets = {}

    # Overlay secrets from file if it exists
    if os.path.exists(path):
        with open(path, 'r') as fh:
            secrets.update(yaml.safe_load(fh) or {})
    else:
        example = path.replace('.yaml', '.example.yaml')
        if os.path.exists(example):
            with open(example, 'r') as fh:
                secrets.update(yaml.safe_load(fh) or {})

    # Environment variables override file values
    secrets.update(_load_from_env())
    return secrets

# generate_token.py

from kiteconnect import KiteConnect
import webbrowser
import yaml

API_KEY = "kut7ix3qpu48c2m1"
API_SECRET = "gzjcxjm6di8txttk0f7p69g8f9zjj0zk"

def save_access_token(token):
    config_path = "config/secrets.yaml"
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    config["kite_access_token"] = token
    with open(config_path, "w") as f:
        yaml.dump(config, f)
    print(f"[✅] Access token saved to {config_path}")

def main():
    kite = KiteConnect(api_key=API_KEY)
    login_url = kite.login_url()
    print("[🔗] Opening login URL in your browser...")
    webbrowser.open(login_url)
    print("[✍️] After login, paste the `request_token` here:")
    request_token = input("Enter request_token: ").strip()

    try:
        data = kite.generate_session(request_token, api_secret=API_SECRET)
        access_token = data["access_token"]
        print(f"[🔐] Access Token: {access_token}")
        save_access_token(access_token)
    except Exception as e:
        print(f"[❌] Failed to generate token: {e}")

if __name__ == "__main__":
    main()

from kiteconnect import KiteConnect
import yaml

from tools.secrets import load_secrets

secrets = load_secrets()
api_key = secrets["kite_api_key"]
api_secret = secrets["kite_api_secret"]

# Initialize KiteConnect
kite = KiteConnect(api_key=api_key)
# Step 1: Print login URL
print("🔐 Login to Zerodha here and authorize the app:")
print(kite.login_url())

# Step 2: After login, paste the request_token here
request_token = input("\nPaste the request_token from the URL here: ").strip()

# Step 3: Generate session (access token)
try:
    data = kite.generate_session(request_token, api_secret=api_secret)
    access_token = data["access_token"]
    print(f"\n✅ Access Token: {access_token}")

    # Step 4: Save to secrets.yaml
    secrets["kite_access_token"] = access_token

    with open("config/secrets.yaml", "w") as f:
        yaml.dump(secrets, f)

    print("✅ Access token saved to config/secrets.yaml")

except Exception as e:
    print(f"❌ Failed to generate access token: {e}")

from SmartApi.smartWebSocketV2 import SmartWebSocketV2
from datetime import datetime

AUTH_TOKEN = "your_auth_token"
API_KEY = "oiSA22HV"
CLIENT_CODE = "your_client_code"
FEED_TOKEN = "your_feed_token"
correlation_id = "abc123"
action = 1  # 1 for subscribe
mode = 1    # 1 for LTP

token_list = [{"exchangeType": 1, "tokens": ["26009"]}]  # Example token

sws = SmartWebSocketV2(AUTH_TOKEN, API_KEY, CLIENT_CODE, FEED_TOKEN)

def on_data(wsapp, message):
    try:
        ltp = message['last_traded_price'] / 100
        timestamp = datetime.fromtimestamp(message['exchange_timestamp'] / 1000)
        print(f"LTP: {ltp} at {timestamp}")
    except Exception as e:
        print(f"Error processing message: {e}")

def on_open(wsapp):
    print("WebSocket connection opened.")
    sws.subscribe(correlation_id, mode, token_list)

def on_error(wsapp, error):
    print(f"WebSocket error: {error}")

def on_close(wsapp):
    print("WebSocket connection closed.")

sws.on_open = on_open
sws.on_data = on_data
sws.on_error = on_error
sws.on_close = on_close

sws.connect()

import os

import adafruit_connection_manager
import wifi
import lib.openai
import adafruit_requests

# Get WiFi details, ensure these are setup in settings.toml
ssid = os.getenv("CIRCUITPY_WIFI_SSID")
password = os.getenv("CIRCUITPY_WIFI_PASSWORD")

# Initalize Wifi, Socket Pool, Request Session
pool = adafruit_connection_manager.get_radio_socketpool(wifi.radio)
ssl_context = adafruit_connection_manager.get_radio_ssl_context(wifi.radio)
requests = adafruit_requests.Session(pool, ssl_context)

print(f"\nConnecting to {ssid}...")
try:
    # Connect to the Wi-Fi network
    wifi.radio.connect(ssid, password)
except OSError as e:
    print(f"❌ OSError: {e}")
print("✅ Wifi connected!")

# OpenAI Chat Completion API
client = lib.openai.OpenAIClient(requests, os.getenv("OPENAI_API_KEY"), base_url=os.getenv("OPENAI_BASE_URL"))

model = "gpt-4o-mini"
messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "What is the meaning of life, according to Douglas Adams?"},
]
print("Sending messages to OpenAI...")
response = client.create_completion(model, messages, max_tokens=100)
print(response)
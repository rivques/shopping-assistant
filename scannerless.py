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

while True:
    # step 0: get input
    upc = input("Enter a UPC: ")
    # step 1: get product page from search
    search_url = f"https://www.googleapis.com/customsearch/v1?q=UPC%3A%20{upc}&key={os.getenv('SEARCH_API_KEY')}&siteSearch=target.com&siteSearchFilter=i&cx=e2d91e113b89b446b"
    search_response = requests.get(search_url)
    print(search_response.json())
    result_page = search_response.json()['items'][0]['link']
    # step two: extract the product name and photo from the result
    product_page = requests.get(result_page)
    print(product_page.text)
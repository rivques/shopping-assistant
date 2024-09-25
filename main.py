import board
import busio
import digitalio
import os
import lib.openai
import adafruit_connection_manager
import wifi

# For most CircuitPython boards:
led = digitalio.DigitalInOut(board.LED)
# For QT Py M0:
# led = digitalio.DigitalInOut(board.SCK)
led.direction = digitalio.Direction.OUTPUT

uart = busio.UART(board.GP16, board.GP17, baudrate=9600)
# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT
# Updated for Circuit Python 9.0
"""WiFi Simpletest"""

import adafruit_requests
print("loading wifi creds...")
# Get WiFi details, ensure these are setup in settings.toml
ssid = os.getenv("CIRCUITPY_WIFI_SSID")
password = os.getenv("CIRCUITPY_WIFI_PASSWORD")
print("loaded wifi creds")

# Initalize Wifi, Socket Pool, Request Session
pool = adafruit_connection_manager.get_radio_socketpool(wifi.radio)
ssl_context = adafruit_connection_manager.get_radio_ssl_context(wifi.radio)
requests = adafruit_requests.Session(pool, ssl_context)
#rssi = wifi.radio.ap_info.rssi

print(f"\nConnecting to {ssid}...")
#print(f"Signal Strength: {rssi}")
wifiConnected=False
while (not wifiConnected) :
    try:
        # Connect to the Wi-Fi network
        wifi.radio.connect(ssid, password)
    except OSError as e:
        print(f"OSError: {e}")
    else:
        print("Wifi!")
        wifiConnected = True
def query(data_string):
    # step 0: get input
    upc = data_string
    # step 1: get product page from search
    search_url = f"http://home.me.rivques.dev:7467/upc2txt/target/{upc}"
    #search_url = f"https://shopping-assistant.rivques.hackclub.app/upc2txt/target/{upc}"
    # search_url = "http://wifitest.adafruit.com/testwifi/index.html"
    print(search_url)
    search_response = requests.get(search_url, headers={"Host": "shopping-assistant.rivques.hackclub.app", "User-Agent": "rivques/1.3.2", "Accept": "*/*"})
    print(search_response.text)
while True:
    data = uart.read(32)  # read up to 32 bytes
    # print(data)  # this is a bytearray type

    if data is not None:
        data_string = ''.join([chr(b) for b in data]) 
        print(data_string, end="")
        query(data_string)
        led.value = False

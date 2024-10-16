# SPDX-FileCopyrightText: 2024 Jeff Epler for Adafruit Industries
#
# SPDX-License-Identifier: MIT

# Stream MP3 audio to I2S decoder
#
# Tested with:
#
#  * Adafruit Metro ESP32-S3
#  * Adafruit Metro ESP32-S2
#  * Adafruit Feather ESP32 V2

import time

import adafruit_connection_manager
import adafruit_requests
import audiobusio
import audiomp3
import board
import wifi
import os

mp3_buffer = bytearray(16384)
mp3_decoder = audiomp3.MP3Decoder("/lib/silence.mp3", mp3_buffer)

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

STREAMING_URL = os.getenv("SERVER_URL") + "/upc2mp3/target/191908973463"

i2s = audiobusio.I2SOut(board.GP3, board.GP4, board.GP2)

with requests.get(STREAMING_URL, headers={"connection": "close"}, stream=True) as response:
    mp3_decoder.file = response.socket
    i2s.play(mp3_decoder)
    while i2s.playing:
        time.sleep(0.1)

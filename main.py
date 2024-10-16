import board
import busio
import digitalio
import os
import time
import adafruit_connection_manager
import wifi
import audiomp3
import audiobusio


mp3_buffer = bytearray(16384)
mp3_decoder = audiomp3.MP3Decoder("/lib/silence.mp3", mp3_buffer)
i2s = audiobusio.I2SOut(board.GP10, board.GP11, board.GP9)

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
    led.value = True
    print(f"fetching from {os.getenv('SERVER_URL')}/upc2mp3/target/{data_string}")
    with requests.get(os.getenv("SERVER_URL") + "/upc2mp3/target/" + data_string, headers={"connection": "close"}, stream=True) as response:
        mp3_decoder.file = response.socket
        i2s.play(mp3_decoder)
        while i2s.playing:
            time.sleep(0.1)
while True:
    data = uart.read(32)  # read up to 32 bytes
    # print(data)  # this is a bytearray type

    if data is not None:
        data_string = ''.join([chr(b) for b in data]) 
        print(data_string, end="")
        query(data_string)
        led.value = False

# Circuitpython on the XIAO nrf52840 
# echo data received over the serial port or over usb to a connected bluetooth device

import board
import busio
import digitalio
import time
from adafruit_ble import BLERadio
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.services.nordic import UARTService

hardware_uart = busio.UART(board.TX, board.RX)

ble = BLERadio()
ble_uart = UARTService()
advertisement = ProvideServicesAdvertisement(ble_uart)

ble.start_advertising(advertisement)

was_connected = False
while True:
    while not ble.connected:
        if was_connected:
            print("Disconnected")
            was_connected = False
    while ble.connected:
        if not was_connected:
            print(f"Connected to {ble.connections[0].address}")
            was_connected = True
        if hardware_uart.in_waiting:
            print(f"Received: {hardware_uart.read(20)}")
            ble_uart.write(hardware_uart.read(20))
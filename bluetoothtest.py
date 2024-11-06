# Circuitpython on the XIAO nrf52840 
# echo data received over the serial port or over usb to a connected bluetooth device

import board
import busio
from adafruit_ble import BLERadio
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.services.nordic import UARTService

hardware_uart = busio.UART(board.TX, board.RX)

ble = BLERadio()
ble_uart = UARTService()
advertisement = ProvideServicesAdvertisement(ble_uart)

ble.start_advertising(advertisement)

was_connected = False
read_data = ""
while True:
    while not ble.connected:
        if was_connected:
            print("Disconnected")
            was_connected = False
    while ble.connected:
        if not was_connected:
            print(f"Connected to {ble.connections[0]}")
            was_connected = True
        if hardware_uart.in_waiting:
            in_char = hardware_uart.read(1)
            if in_char == b"\r":
                print(f"Got \\r, sending...s")
                ble_uart.write(read_data)
                print(f"Sent: {read_data}")
                read_data = ""
            else:
                read_data += in_char.decode("utf-8")
                print(f"Read so far: {read_data}")
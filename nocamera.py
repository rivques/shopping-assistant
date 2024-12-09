# Circuitpython on the XIAO nrf52840 
# echo data received over the serial port or over usb to a connected bluetooth device

import board
import digitalio
import busio
from adafruit_ble import BLERadio
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.services.nordic import UARTService
import time

button = digitalio.DigitalInOut(board.D3)
button.direction = digitalio.Direction.INPUT
button.pull = digitalio.Pull.UP

# camera_power = digitalio.DigitalInOut(board.D4)
# camera_power.direction = digitalio.Direction.OUTPUT
# camera_power.value = False

hardware_uart = busio.UART(board.TX, board.RX)

ble = BLERadio()
ble_uart = UARTService()
advertisement = ProvideServicesAdvertisement(ble_uart)

ble.start_advertising(advertisement)

is_down = False
last_down = time.monotonic()
down_handled = False
camera_last_on = time.monotonic()
def handle_button():
    #print("Handling button")
    # if the button has been down for more than 1 second and we're connected, disconnect and start advertising again
    global is_down, last_down, down_handled, camera_last_on
    if button.value:
        if is_down:
            is_down = False
            down_handled = False
            # button was just released
            print("Button up")
            # if button was down for less than 0.5 seconds, turn on camera
            if time.monotonic() - last_down < 0.5:
                print("Button was down for less than 0.5 seconds")
                # camera_power.value = True
                ble_uart.write("198101598295")
                camera_last_on = time.monotonic()

    else:
        if not is_down:
            print("Button down")
            is_down = True
            last_down = time.monotonic()
        elif time.monotonic() - last_down > 1 and not down_handled:
            down_handled = True
            # button has been down for more than 1 second
            print("Button down for more than 1 second")
            if ble.connected:
                print("Disconnecting")
                for connection in ble.connections:
                    print(f"Disconnecting from {connection}")
                    connection.disconnect()
                ble.stop_advertising()
                ble.start_advertising(advertisement)

def check_turn_camera_off():
    return # no camera
    global camera_last_on
    # keep the camera on for 10 seconds after the last button press
    if time.monotonic() - camera_last_on > 10 and camera_power.value:
        camera_power.value = False
        print("Turning camera off")

was_connected = False
read_data = ""
while True:
    handle_button()
    check_turn_camera_off()
    while not ble.connected:
        handle_button()
        check_turn_camera_off()
        if was_connected:
            print("Disconnected")
            was_connected = False
            try:
                ble.start_advertising(advertisement)
            except:
                pass # already advertising
    while ble.connected:
        handle_button()
        check_turn_camera_off()
        if not was_connected:
            print(f"Connected to {ble.connections[0]}")
            was_connected = True
        if hardware_uart.in_waiting:
            in_char = hardware_uart.read(1)
            if in_char == b"\r":
                print(f"Got \\r, sending data...")
                ble_uart.write(read_data)
                print(f"Sent: {read_data}")
                read_data = ""
            else:
                read_data += in_char.decode("utf-8")
                print(f"Read so far: {read_data}")
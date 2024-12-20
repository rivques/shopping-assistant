# SPDX-FileCopyrightText: 2018 Kattni Rembor for Adafruit Industries
#
# SPDX-License-Identifier: MIT

# Example for how to play a tone using the Raspberry Pi Pico and the MAX98357 breakout board.
# Derived from: https://learn.adafruit.com/adafruit-max98357-i2s-class-d-mono-amp/circuitpython-wiring-test
#
# See README.md for notes.

import time
import array
import math
import audiocore
import board
import audiobusio

sample_rate = 8000
tone_volume = 0.1  # Increase or decrease this to adjust the volume of the tone.
frequency = 440  # Set this to the Hz of the tone you want to generate.
length = sample_rate // frequency  # One freqency period
sine_wave = array.array("H", [0] * length)
for i in range(length):
    sine_wave[i] = int((math.sin(math.pi * 2 * frequency * i / sample_rate) *
                        tone_volume + 1) * (2 ** 15 - 1))

# For Raspberry Pi Pico(bit_clock_pin, word_select_pin, data_pin, ...)
audio = audiobusio.I2SOut(board.GP10, board.GP11, board.GP9)

# For Feather M0 Express, ItsyBitsy M0 Express, Metro M0 Express
# audio = audiobusio.I2SOut(board.D1, board.D0, board.D9)
# For Feather M4 Express
# audio = audiobusio.I2SOut(board.D1, board.D10, board.D11)
# For Metro M4 Express
# audio = audiobusio.I2SOut(board.D3, board.D9, board.D8)
sine_wave_sample = audiocore.RawSample(sine_wave, sample_rate=sample_rate)

while True:
    audio.play(sine_wave_sample, loop=True)
    time.sleep(1)
    audio.stop()
    time.sleep(1)
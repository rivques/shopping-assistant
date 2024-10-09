# 2024-10-09
## Probing Bluetooth sound sink with oscilloscope
When no audio playing: All 3 lines 0 V
When audio playing: PHY12/DIN 200-210kHz square wave phase varying, PHY14/BCLK 1.411 MHz square wave, PHY15/LRC 44.1kHz square wave (implies 44.1kHz audio, 16 bits per channel, 2 channels)
No tone heard
Config: PICO_AUDIO_I2S_DATA_PIN=9, PICO_AUDIO_I2S_CLOCK_PIN_BASE=10
## Probing I2S tone test
When no audio playing: All 3 lines 0V
When audio playing: PHY12/DIN 27-23kHz square wave phase varying, PHY14/BCLK 209kHzish square wave, PHY15/LRC 6KHzish (implies 6kHzish audio, 16 bits per channel, 2 channels, actual sample rate 8kHz)
Audio distorted or mangled when PHY15 touched by probe
No audio when PHY14 touched by probe
Config: audiobusio.I2SOut(board.GP10, board.GP11, board.GP9)
## Trying Bluetooth again w/o probes
Still no audio at any volume

## Idea: lower sample rate in Bluetooth version, that's the most significant difference I see. The werid behavoir when I touch it with a probe makes me think it might be an impedance thing, and 44.1kHz is unfavorable for my setup.
can't find the place where sample rate is set though...

#include "AudioTools.h"
#include "BTstack_A2DP.h"

// #define PIN_I2S_BCK 26
// #define PIN_I2S_WS 27 // aka LRC
// #define PIN_I2S_DATA_OUT 28
I2SStream out;

void setup() {
  Serial.begin(115200);
  waitFor(Serial);
  AudioLogger::instance().begin(Serial, AudioLogger::Info);

  A2DPSink.setVolume(50);
  A2DPSink.begin(out, "rp2040");
}

void loop() {}
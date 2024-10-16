# Problems we need to solve:
* How will we build the app?
    * Probably with Flutter and flutter_blue_plus
* How will we stream the mp3 data over Bluetooth?
   * We'll set up the Pico as an A2DP Sink with [RP2040-A2DP](https://github.com/pschatzmann/RP2040-A2DP), which will allow it to pair as a speaker to the phone. We'll then have the Flutter app play the audio description over the Pico.
* How will we power the Pico?
    * With a rechargable LiIon battery

import 'package:flutter/material.dart';
import 'package:flutter_blue_plus/flutter_blue_plus.dart';
import 'package:path_provider/path_provider.dart';
import 'package:http/http.dart' as http;
import 'package:just_audio/just_audio.dart';
import 'dart:io';
import 'package:haptic_feedback/haptic_feedback.dart';

void main() => runApp(const MyApp());

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Shopping Assistant',
      theme: ThemeData(
        primarySwatch: Colors.blue,
      ),
      home: const BLEAudioPage(),
    );
  }
}

class BLEAudioPage extends StatefulWidget {
  const BLEAudioPage({super.key});

  @override
  _BLEAudioPageState createState() => _BLEAudioPageState();
}

class _BLEAudioPageState extends State<BLEAudioPage> {
  final player = AudioPlayer();
  final TextEditingController _urlController = TextEditingController();
  BluetoothDevice? connectedDevice;
  BluetoothCharacteristic? uartCharacteristic;
  String receivedUrl = '';

  @override
  void initState() {
    super.initState();
    connectToDevice();
  }

  // BLE connection logic
  void connectToDevice() async {
    FlutterBluePlus.setLogLevel(LogLevel.verbose, color: false);
    FlutterBluePlus.startScan(timeout: const Duration(seconds: 4));
    print('Scanning for Bluetooth devices...');

    // Scan for the nRF52840 device
    FlutterBluePlus.scanResults.listen((results) async {
      print('Scan listener called');
      for (ScanResult r in results) {
        print(
            'Found Bluetooth scan result: ${r.device.advName} with platform: ${r.device.platformName}');
        if (r.device.platformName.startsWith("CIRCUITPY")) {
          print('Found nRF52840 device');
          FlutterBluePlus.stopScan();
          print("Connecting to device...");
          await r.device.connect();
          print("Connected to device");
          setState(() {
            connectedDevice = r.device;
          });
          print("Discovering services...");
          discoverServices(r.device);
          // on disconnect, set connectedDevice to null
          r.device.connectionState.listen((state) {
            if (state == BluetoothConnectionState.disconnected) {
              setState(() {
                connectedDevice = null;
              });
            }
          });
          break;
        }
      }
    });
  }

  void discoverServices(BluetoothDevice device) async {
    List<BluetoothService> services = await device.discoverServices();
    for (BluetoothService service in services) {
      if (service.uuid.toString().toUpperCase() ==
          "6E400001-B5A3-F393-E0A9-E50E24DCCA9E") {
        for (BluetoothCharacteristic c in service.characteristics) {
          if (c.uuid.toString().toUpperCase() ==
              "6E400003-B5A3-F393-E0A9-E50E24DCCA9E") {
            await c.setNotifyValue(true);
            c.value.listen((value) {
              onDataReceived(value);
            });
            print("Configured listener");
            setState(() {
              uartCharacteristic = c;
            });
          }
        }
      }
    }
  }

  // Handle receiving data from UART
  void onDataReceived(List<int> data) {
    print("Recieved data:");
    String datastring = String.fromCharCodes(data);
    print(datastring);
    if (datastring.isNotEmpty) {
      Haptics.vibrate(HapticsType.success);
      String url =
          'https://alert-rooster-accepted.ngrok-free.app/upc2mp3/target/$datastring';
      setState(() {
        receivedUrl = url;
      });
      fetchAndPlayAudio(url);
    }
  }

  // HTTP request and audio playback logic
  void fetchAndPlayAudio(String url) async {
    try {
      playAudioFromUrl(url);
      // final response = await http.get(Uri.parse(url));
      // if (response.statusCode == 200) {
      //   playAudioFromUrl(url);
      // } else {
      //   print('Failed to load audio file');
      // }
    } catch (e) {
      print('Error: $e');
    }
  }

  void playAudioFromUrl(String url) async {
    print('Playing audio from URL: $url');
    final response = await http.get(Uri.parse(url));
    print('Response status: ${response.statusCode}');
    final directory = await getTemporaryDirectory();
    final filePath = '${directory.path}/temp.mp3';
    print('Writing audio file to: $filePath');
    final file = File(filePath);
    await file.writeAsBytes(response.bodyBytes);
    print('File written');
    try {
      await player.setFilePath(filePath);
      player.play();
    } catch (e) {
      print('Error: $e');
    }
    print('file path set');
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("Shopping Assistant"),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            ElevatedButton(
              onPressed: () {
                if (connectedDevice != null) {
                connectedDevice!.disconnect();
                } else {
                connectToDevice();
                }
              },
              child: Text(connectedDevice != null ? 'Disconnect from Device' : 'Connect to Device'),
            ),
            const SizedBox(height: 20),
            Text(
              'Connection status: ${connectedDevice != null ? "Connected" : "Not Connected"}',
              style: const TextStyle(fontSize: 18),
            ),
            const SizedBox(height: 20),
            if (receivedUrl.isNotEmpty) ...[
              Text(
              'Playing URL: $receivedUrl',
              style: const TextStyle(fontSize: 16),
              ),
              const SizedBox(height: 10),
            ],
            // Slider for playback speed
            const Text('Playback Speed'),
            Row(
              children: [
                Text('${player.speed.toStringAsFixed(2)}x'),
                Expanded(
                  child: Slider(
                    value: player.speed,
                    min: 0.5,
                    max: 2,
                    divisions: 6,
                    label: '${player.speed.toString()}x',
                    onChanged: (value) {
                      player.setSpeed(value);
                      Haptics.vibrate(HapticsType.selection);
                      setState(() {}); // Refresh to update the displayed value
                    },
                  ),
                )
              ],
            ),
            if (player.playing)
              ElevatedButton(
                onPressed: () async {
                  player.stop();
                },
                child: const Text('Stop Audio'),
              ),
          ],
        ),
      ),
    );
  }
}

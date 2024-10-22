import 'package:flutter/material.dart';
import 'package:flutter_blue_plus/flutter_blue_plus.dart';
import 'package:http/http.dart' as http;
import 'package:audioplayers/audioplayers.dart';

void main() => runApp(MyApp());

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'BLE Audio Player',
      theme: ThemeData(
        primarySwatch: Colors.blue,
      ),
      home: BLEAudioPage(),
    );
  }
}

class BLEAudioPage extends StatefulWidget {
  @override
  _BLEAudioPageState createState() => _BLEAudioPageState();
}

class _BLEAudioPageState extends State<BLEAudioPage> {
  BluetoothDevice? connectedDevice;
  BluetoothCharacteristic? uartCharacteristic;
  String receivedUrl = '';
  AudioPlayer audioPlayer = AudioPlayer();

  @override
  void initState() {
    super.initState();
    connectToDevice();
  }

  // BLE connection logic
  void connectToDevice() async {
    FlutterBluePlus.startScan(timeout: Duration(seconds: 4));

    // Scan for the nRF52840 device
    FlutterBluePlus.scanResults.listen((results) {
      for (ScanResult r in results) {
        if (r.device.name == "nRF52840") {
          FlutterBluePlus.stopScan();
          r.device.connect();
          setState(() {
            connectedDevice = r.device;
          });
          discoverServices(r.device);
          break;
        }
      }
    });
  }

  void discoverServices(BluetoothDevice device) async {
    List<BluetoothService> services = await device.discoverServices();
    for (BluetoothService service in services) {
      if (service.uuid.toString() == "6E400001-B5A3-F393-E0A9-E50E24DCCA9E") {
        for (BluetoothCharacteristic c in service.characteristics) {
          if (c.uuid.toString() == "6E400002-B5A3-F393-E0A9-E50E24DCCA9E") {
            await c.setNotifyValue(true);
            c.value.listen((value) {
              onDataReceived(value);
            });
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
    String url = String.fromCharCodes(data);
    if (url.isNotEmpty) {
      setState(() {
        receivedUrl = url;
      });
      fetchAndPlayAudio(url);
    }
  }

  // HTTP request and audio playback logic
  void fetchAndPlayAudio(String url) async {
    try {
      final response = await http.get(Uri.parse(url));
      if (response.statusCode == 200) {
        playAudioFromUrl(url);
      } else {
        print('Failed to load audio file');
      }
    } catch (e) {
      print('Error: $e');
    }
  }

  void playAudioFromUrl(String url) async {
    await audioPlayer.play(UrlSource(url));
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text("BLE Audio Player"),
      ),
      body: Padding(
        padding: EdgeInsets.all(16.0),
        child: Column(
          children: [
            Text(
              'Connection status: ${connectedDevice != null ? "Connected" : "Not Connected"}',
              style: TextStyle(fontSize: 18),
            ),
            SizedBox(height: 20),
            Text(
              'Received URL: $receivedUrl',
              style: TextStyle(fontSize: 16),
            ),
            SizedBox(height: 20),
            ElevatedButton(
              onPressed: () async {
                if (receivedUrl.isNotEmpty) {
                  fetchAndPlayAudio(receivedUrl);
                }
              },
              child: Text('Play Received Audio'),
            ),
          ],
        ),
      ),
    );
  }
}

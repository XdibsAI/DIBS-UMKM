import 'package:flutter/material.dart';
import '../../services/printer_service.dart';

class PrinterSetupScreen extends StatefulWidget {
  const PrinterSetupScreen({super.key});

  @override
  State<PrinterSetupScreen> createState() => _PrinterSetupScreenState();
}

class _PrinterSetupScreenState extends State<PrinterSetupScreen> {
  List devices = [];

  @override
  void initState() {
    super.initState();
    loadDevices();
  }

  Future<void> loadDevices() async {
    final result = await PrinterService.getDevices();
    setState(() {
      devices = result;
    });
  }

  Future<void> connectPrinter(String mac) async {
    final ok = await PrinterService.connect(mac);

    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(ok ? 'Printer connected' : 'Failed connect'),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Printer POS')),
      body: ListView.builder(
        itemCount: devices.length,
        itemBuilder: (_, i) {
          final d = devices[i];
          return ListTile(
            title: Text(d.name),
            subtitle: Text(d.macAdress),
            trailing: ElevatedButton(
              onPressed: () => connectPrinter(d.macAdress),
              child: const Text('Connect'),
            ),
          );
        },
      ),
    );
  }
}

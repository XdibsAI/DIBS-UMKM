import 'package:print_bluetooth_thermal/print_bluetooth_thermal.dart';
import 'package:esc_pos_utils_plus/esc_pos_utils_plus.dart';

class PrinterService {
  static Future<List<BluetoothInfo>> getDevices() async {
    return await PrintBluetoothThermal.pairedBluetooths;
  }

  static Future<bool> connect(String mac) async {
    return await PrintBluetoothThermal.connect(macPrinterAddress: mac);
  }

  static Future<void> printReceipt({
    required List<Map<String, dynamic>> items,
    required int total,
    required String paymentMethod,
  }) async {
    final profile = await CapabilityProfile.load();
    final generator = Generator(PaperSize.mm58, profile);

    List<int> bytes = [];

    bytes += generator.text(
      'TOKO UMKM',
      styles: const PosStyles(
        align: PosAlign.center,
        bold: true,
        height: PosTextSize.size2,
        width: PosTextSize.size2,
      ),
    );

    bytes += generator.hr();

    for (final item in items) {
      bytes += generator.row([
        PosColumn(
          text: item['name'],
          width: 8,
        ),
        PosColumn(
          text: 'x${item['quantity']}',
          width: 2,
        ),
        PosColumn(
          text: '${item['subtotal']}',
          width: 2,
        ),
      ]);
    }

    bytes += generator.hr();

    bytes += generator.row([
      PosColumn(text: 'TOTAL', width: 6),
      PosColumn(
        text: 'Rp $total',
        width: 6,
        styles: const PosStyles(align: PosAlign.right, bold: true),
      ),
    ]);

    bytes += generator.text(
      'Metode: $paymentMethod',
      styles: const PosStyles(align: PosAlign.center),
    );

    bytes += generator.feed(2);
    bytes += generator.cut();

    await PrintBluetoothThermal.writeBytes(bytes);
  }
}

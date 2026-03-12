import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/toko_provider.dart';

class InclusiveCheckoutScreen extends StatefulWidget {
  const InclusiveCheckoutScreen({Key? key}) : super(key: key);

  @override
  State<InclusiveCheckoutScreen> createState() =>
      _InclusiveCheckoutScreenState();
}

class _InclusiveCheckoutScreenState extends State<InclusiveCheckoutScreen> {
  final TextEditingController _voiceInputController = TextEditingController();
  bool _isProcessing = false;

  @override
  void dispose() {
    _voiceInputController.dispose();
    super.dispose();
  }

  Future<void> _processVoice() async {
    if (_voiceInputController.text.trim().isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Mohon masukkan teks atau gunakan suara')),
      );
      return;
    }

    setState(() => _isProcessing = true);

    try {
      final provider = context.read<TokoProvider>();
      await provider.processVoiceScan(_voiceInputController.text);

      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('✅ Produk berhasil ditambahkan ke keranjang'),
          backgroundColor: Colors.green,
        ),
      );

      _voiceInputController.clear();
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('❌ Error: $e'), backgroundColor: Colors.red),
      );
    } finally {
      setState(() => _isProcessing = false);
    }
  }

  void _showReceiptDialog(TokoProvider provider) {
    final cart = provider.cart;
    final total = provider.cartTotal;

    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('📄 Rincian Belanja'),
        content: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              ...cart.map((item) => Padding(
                    padding: const EdgeInsets.symmetric(vertical: 4),
                    child: Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Expanded(
                          child: Text(
                            '${item['quantity']}x ${item['name']}',
                            style: const TextStyle(fontSize: 14),
                          ),
                        ),
                        Text(
                          'Rp ${item['price'] * item['quantity']}',
                          style: const TextStyle(fontWeight: FontWeight.bold),
                        ),
                      ],
                    ),
                  )),
              const Divider(thickness: 2, height: 20),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  const Text(
                    'TOTAL',
                    style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                  ),
                  Text(
                    'Rp $total',
                    style: const TextStyle(
                      fontSize: 20,
                      fontWeight: FontWeight.bold,
                      color: Colors.green,
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text('Tutup'),
          ),
          ElevatedButton.icon(
            onPressed: () {
              // TODO: Implement actual print
              Navigator.pop(ctx);
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('📄 Struk dicetak (simulasi)')),
              );
            },
            icon: const Icon(Icons.print),
            label: const Text('Cetak'),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Theme.of(context).scaffoldBackgroundColor,
      appBar: AppBar(
        backgroundColor: Theme.of(context).primaryColor,
        title: Row(
          children: [
            Icon(Icons.accessibility_new,
                color: Theme.of(context).colorScheme.primary),
            const SizedBox(width: 8),
            const Text('Mode Inklusif'),
          ],
        ),
      ),
      body: Consumer<TokoProvider>(
        builder: (context, provider, child) {
          return SingleChildScrollView(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                // Header Instructions
                Container(
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: Colors.blue.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(color: Colors.blue.withOpacity(0.3)),
                  ),
                  child: Column(
                    children: const [
                      Icon(Icons.mic, size: 48, color: Colors.blue),
                      SizedBox(height: 8),
                      Text(
                        '🎤 Silakan Bicara untuk Berbelanja',
                        style: TextStyle(
                            fontSize: 18, fontWeight: FontWeight.bold),
                        textAlign: TextAlign.center,
                      ),
                      SizedBox(height: 8),
                      Text(
                        'Contoh: "2 keripik pisang 1 cireng"',
                        style: TextStyle(fontSize: 14, color: Colors.grey),
                        textAlign: TextAlign.center,
                      ),
                    ],
                  ),
                ),

                const SizedBox(height: 24),

                // Voice Input (Manual for demo)
                TextField(
                  controller: _voiceInputController,
                  decoration: InputDecoration(
                    labelText: 'Teks Suara (atau ketik manual)',
                    hintText: 'Contoh: 2 keripik pisang 1 cireng',
                    border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(12)),
                    prefixIcon: const Icon(Icons.keyboard_voice),
                  ),
                  maxLines: 2,
                  enabled: !_isProcessing,
                ),

                const SizedBox(height: 16),

                // Scan Button
                ElevatedButton.icon(
                  onPressed: _isProcessing ? null : _processVoice,
                  icon: _isProcessing
                      ? const SizedBox(
                          width: 20,
                          height: 20,
                          child: CircularProgressIndicator(
                              strokeWidth: 2, color: Colors.white),
                        )
                      : const Icon(Icons.send),
                  label:
                      Text(_isProcessing ? 'Memproses...' : 'Proses Belanja'),
                  style: ElevatedButton.styleFrom(
                    padding: const EdgeInsets.symmetric(vertical: 16),
                    backgroundColor: Theme.of(context).colorScheme.primary,
                    foregroundColor: Colors.white,
                  ),
                ),

                const SizedBox(height: 24),

                // Last Voice Text
                if (provider.lastVoiceText.isNotEmpty)
                  Container(
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: Colors.green.withOpacity(0.1),
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Row(
                      children: [
                        const Icon(Icons.check_circle, color: Colors.green),
                        const SizedBox(width: 8),
                        Expanded(
                          child: Text(
                            'Terakhir: "${provider.lastVoiceText}"',
                            style: const TextStyle(fontSize: 12),
                          ),
                        ),
                      ],
                    ),
                  ),

                const SizedBox(height: 24),

                // Cart Section
                Text(
                  '🛒 Keranjang Belanja',
                  style: TextStyle(
                    fontSize: 20,
                    fontWeight: FontWeight.bold,
                    color: Theme.of(context).textTheme.bodyLarge!.color,
                  ),
                ),

                const SizedBox(height: 12),

                if (provider.cart.isEmpty)
                  Container(
                    padding: const EdgeInsets.all(32),
                    child: Column(
                      children: const [
                        Icon(Icons.shopping_cart_outlined,
                            size: 64, color: Colors.grey),
                        SizedBox(height: 8),
                        Text(
                          'Keranjang masih kosong',
                          style: TextStyle(color: Colors.grey),
                        ),
                      ],
                    ),
                  )
                else
                  ...provider.cart.map((item) => Card(
                        margin: const EdgeInsets.only(bottom: 8),
                        child: ListTile(
                          leading: CircleAvatar(
                            backgroundColor:
                                Theme.of(context).colorScheme.primary,
                            child: Text(
                              '${item['quantity']}',
                              style: const TextStyle(
                                  color: Colors.white,
                                  fontWeight: FontWeight.bold),
                            ),
                          ),
                          title: Text(item['name']),
                          subtitle: Text('@ Rp ${item['price']}'),
                          trailing: Text(
                            'Rp ${item['price'] * item['quantity']}',
                            style: const TextStyle(
                                fontWeight: FontWeight.bold, fontSize: 16),
                          ),
                        ),
                      )),

                if (provider.cart.isNotEmpty) ...[
                  const SizedBox(height: 16),
                  const Divider(thickness: 2),
                  const SizedBox(height: 8),

                  // Total
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      const Text(
                        'TOTAL',
                        style: TextStyle(
                            fontSize: 20, fontWeight: FontWeight.bold),
                      ),
                      Text(
                        'Rp ${provider.cartTotal}',
                        style: const TextStyle(
                          fontSize: 24,
                          fontWeight: FontWeight.bold,
                          color: Colors.green,
                        ),
                      ),
                    ],
                  ),

                  const SizedBox(height: 24),

                  // Action Buttons
                  Row(
                    children: [
                      Expanded(
                        child: OutlinedButton.icon(
                          onPressed: () => _showReceiptDialog(provider),
                          icon: const Icon(Icons.receipt_long),
                          label: const Text('Lihat Rincian'),
                        ),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: ElevatedButton.icon(
                          onPressed: () {
                            provider.clearCart();
                            ScaffoldMessenger.of(context).showSnackBar(
                              const SnackBar(
                                  content: Text('✅ Keranjang dikosongkan')),
                            );
                          },
                          icon: const Icon(Icons.clear_all),
                          label: const Text('Clear'),
                          style: ElevatedButton.styleFrom(
                              backgroundColor: Colors.red),
                        ),
                      ),
                    ],
                  ),
                ],
              ],
            ),
          );
        },
      ),
    );
  }
}

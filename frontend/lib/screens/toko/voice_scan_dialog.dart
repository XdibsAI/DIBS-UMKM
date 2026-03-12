import 'package:flutter/material.dart';
import 'package:speech_to_text/speech_to_text.dart' as stt;
import 'dart:async';

class VoiceScanDialog extends StatefulWidget {
  const VoiceScanDialog({super.key});
  @override
  State<VoiceScanDialog> createState() => _VoiceScanDialogState();
}

class _VoiceScanDialogState extends State<VoiceScanDialog> {
  late stt.SpeechToText _speech;
  bool _isListening = false;
  String _text = "";
  double _soundLevel = 0.0;
  Timer? _stopTimer;

  @override
  void initState() {
    super.initState();
    _speech = stt.SpeechToText();
    _startListening();
  }

  void _startListening() async {
    bool available = await _speech.initialize();
    if (available) {
      setState(() => _isListening = true);
      _speech.listen(
        onResult: (val) {
          setState(() {
            _text = val.recognizedWords;
          });

          // --- AUTO SUBMIT LOGIC ---
          // Jika user berhenti ngomong selama 1.5 detik, otomatis proses
          _stopTimer?.cancel();
          _stopTimer = Timer(const Duration(milliseconds: 1500), () {
            if (_text.isNotEmpty) {
              _speech.stop();
              Navigator.pop(context, _text);
            }
          });
        },
        onSoundLevelChange: (level) => setState(() => _soundLevel = level),
      );
    }
  }

  @override
  void dispose() {
    _stopTimer?.cancel();
    _speech.stop();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(24),
      decoration: const BoxDecoration(
        color: Color(0xFF1A1A2E),
        borderRadius: BorderRadius.vertical(top: Radius.circular(30)),
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          const Text("Dibs Voice Monitor",
              style: TextStyle(
                  color: Colors.cyanAccent, fontWeight: FontWeight.bold)),
          const SizedBox(height: 25),

          // Visualizer yang membesar sesuai volume
          AnimatedContainer(
            duration: const Duration(milliseconds: 100),
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              boxShadow: [
                BoxShadow(
                  color: Colors.redAccent.withOpacity(0.5),
                  blurRadius: _soundLevel * 4,
                  spreadRadius: _soundLevel,
                )
              ],
            ),
            child: const CircleAvatar(
              radius: 35,
              backgroundColor: Colors.redAccent,
              child: Icon(Icons.mic, color: Colors.white, size: 40),
            ),
          ),

          const SizedBox(height: 25),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 15, vertical: 10),
            decoration: BoxDecoration(
              color: Colors.white.withOpacity(0.05),
              borderRadius: BorderRadius.circular(15),
              border: Border.all(color: Colors.cyanAccent.withOpacity(0.3)),
            ),
            child: Text(
              _text.isEmpty ? "Mendengarkan..." : _text,
              style: const TextStyle(color: Colors.white, fontSize: 18),
              textAlign: TextAlign.center,
            ),
          ),
          const SizedBox(height: 15),
          const Text("Diam sejenak untuk memproses otomatis",
              style: TextStyle(color: Colors.grey, fontSize: 12)),
          const SizedBox(height: 20),
          TextButton(
            onPressed: () => Navigator.pop(context),
            child:
                const Text("Batal", style: TextStyle(color: Colors.redAccent)),
          ),
        ],
      ),
    );
  }
}

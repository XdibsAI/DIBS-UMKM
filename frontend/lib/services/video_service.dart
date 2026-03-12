import 'dart:io';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import 'package:permission_handler/permission_handler.dart';

class VideoService {
  static Future<bool> _requestStoragePermission() async {
    if (!Platform.isAndroid) return true;

    final manage = await Permission.manageExternalStorage.request();
    if (manage.isGranted) return true;

    final media = await Permission.videos.request();
    if (media.isGranted) return true;

    final storage = await Permission.storage.request();
    if (storage.isGranted) return true;

    return false;
  }

  static Future<Directory> _ensureVideoDir() async {
    final dir = Directory('/storage/emulated/0/Movies/DIBS');
    if (!await dir.exists()) {
      await dir.create(recursive: true);
    }
    return dir;
  }

  static String _safeFileName(String input) {
    var name = input.trim();
    if (name.isEmpty) {
      name = 'video_${DateTime.now().millisecondsSinceEpoch}.mp4';
    }
    name = name
        .replaceAll(RegExp(r'[<>:"/\\|?*]'), '_')
        .replaceAll(RegExp(r'\s+'), '_');
    if (!name.toLowerCase().endsWith('.mp4')) {
      name = '$name.mp4';
    }
    return name;
  }

  static Future<String> downloadVideo({
    required String url,
    String? fileName,
    String? bearerToken,
  }) async {
    final ok = await _requestStoragePermission();
    if (!ok) {
      throw Exception('Izin penyimpanan ditolak');
    }

    final dir = await _ensureVideoDir();
    final finalName = _safeFileName(fileName ?? '');
    final savePath = '${dir.path}/$finalName';

    final headers = <String, String>{};
    if (bearerToken != null && bearerToken.trim().isNotEmpty) {
      headers['Authorization'] = 'Bearer ${bearerToken.trim()}';
    }

    final response = await http.get(Uri.parse(url), headers: headers);
    if (response.statusCode < 200 || response.statusCode >= 300) {
      throw Exception('HTTP ${response.statusCode}');
    }

    final file = File(savePath);
    await file.writeAsBytes(response.bodyBytes, flush: true);

    final size = await file.length();
    if (size < 1024) {
      throw Exception('File video terlalu kecil / tidak valid');
    }

    debugPrint('Video saved to: $savePath');
    return savePath;
  }
}

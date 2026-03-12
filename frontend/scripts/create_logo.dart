import 'dart:io';
import 'package:image/image.dart' as img;

void main() {
  print('🎨 Menggenerate logo baru untuk Dibs...');

  // 1. Buat kanvas (512x512) dengan parameter bernama
  // Library image versi terbaru mewajibkan width dan height sebagai named parameters
  final image = img.Image(width: 512, height: 512);

  // 2. Isi background (Hitam Gelap/Dark Mode)
  img.fill(image, color: img.ColorRgb8(18, 18, 18));

  // 3. Gambar Lingkaran Hijau (Aura Icon)
  img.drawCircle(image,
      x: 256, y: 256, radius: 200, color: img.ColorRgb8(0, 255, 128));

  // 4. Tambahkan Teks "D1" di tengah
  // Menggunakan arial48 bawaan library yang stabil
  img.drawString(image, 'D1',
      font: img.arial48, x: 225, y: 230, color: img.ColorRgb8(255, 255, 255));

  // 5. Simpan hasil ke folder assets
  final logoPath = 'assets/images/logo.png';
  final foregroundPath = 'assets/images/logo_foreground.png';

  Directory('assets/images').createSync(recursive: true);

  File(logoPath).writeAsBytesSync(img.encodePng(image));

  // Buat versi foreground (sedikit lebih kecil untuk adaptif icon)
  final foreground = img.copyResize(image, width: 432, height: 432);
  File(foregroundPath).writeAsBytesSync(img.encodePng(foreground));

  print('✅ Logo berhasil dibuat: $logoPath');
}

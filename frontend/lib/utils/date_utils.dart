// FIXED: pastikan parameter nullable ditangani dengan aman
String formatTimestamp(String? timestamp) {
  if (timestamp == null) return '';

  try {
    // Parse as UTC
    final utc = DateTime.parse(timestamp).toUtc();

    // Convert to local timezone
    final local = utc.toLocal();

    // Format sesuai kebutuhan
    final now = DateTime.now();
    final today = DateTime(now.year, now.month, now.day);
    final dateToCheck = DateTime(local.year, local.month, local.day);

    if (dateToCheck == today) {
      // Today: show time only
      return '${local.hour.toString().padLeft(2, '0')}:${local.minute.toString().padLeft(2, '0')}';
    } else if (dateToCheck == today.subtract(const Duration(days: 1))) {
      // Yesterday
      return 'Kemarin ${local.hour.toString().padLeft(2, '0')}:${local.minute.toString().padLeft(2, '0')}';
    } else if (now.difference(local).inDays < 7) {
      // This week: show day name
      final days = ['Sen', 'Sel', 'Rab', 'Kam', 'Jum', 'Sab', 'Min'];
      return '${days[local.weekday - 1]} ${local.hour.toString().padLeft(2, '0')}:${local.minute.toString().padLeft(2, '0')}';
    } else {
      // Older: show full date
      return '${local.day}/${local.month}/${local.year} ${local.hour.toString().padLeft(2, '0')}:${local.minute.toString().padLeft(2, '0')}';
    }
  } catch (e) {
    return timestamp;
  }
}

// FIXED: tambahkan penanganan null di awal fungsi
String formatDate(String? timestamp) {
  if (timestamp == null) return '';

  try {
    final utc = DateTime.parse(timestamp).toUtc();
    final local = utc.toLocal();
    return '${local.day}/${local.month}/${local.year}';
  } catch (e) {
    return timestamp;
  }
}

// FIXED: pastikan format datetime konsisten dengan fungsi lain
String formatDateTime(String? timestamp) {
  if (timestamp == null) return '';

  try {
    final utc = DateTime.parse(timestamp).toUtc();
    final local = utc.toLocal();
    return '${local.day}/${local.month}/${local.year} ${local.hour.toString().padLeft(2, '0')}:${local.minute.toString().padLeft(2, '0')}';
  } catch (e) {
    return timestamp;
  }
}

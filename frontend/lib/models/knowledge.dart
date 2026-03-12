class Knowledge {
  final int id;
  final String content;
  final String category;
  final List<String> tags;
  final String? filePath;
  final String? fileType;
  final DateTime createdAt;

  Knowledge({
    required this.id,
    required this.content,
    this.category = 'general',
    this.tags = const [],
    this.filePath,
    this.fileType,
    required this.createdAt,
  });

  factory Knowledge.fromJson(Map<String, dynamic> json) {
    return Knowledge(
      id: json['id'] ?? 0,
      content: json['content'] ?? '',
      category: json['category'] ?? 'general',
      tags: json['tags'] != null ? List<String>.from(json['tags']) : [],
      filePath: json['file_path'],
      fileType: json['file_type'],
      createdAt: DateTime.parse(
          json['created_at'] ?? DateTime.now().toIso8601String()),
    );
  }

  String get typeIcon {
    if (fileType != null) {
      if (fileType!.contains('image')) return '🖼️';
      if (fileType!.contains('pdf')) return '📄';
      if (fileType!.contains('doc')) return '📝';
    }
    return '📌';
  }
}

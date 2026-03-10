class VideoProject {
  final String id;
  final String niche;
  final String? title;
  final int duration;
  final String status;
  final String? videoPath;
  final String? downloadUrl;
  final String style;
  final String language;
  final Map<String, dynamic>? script;

  VideoProject({
    required this.id,
    required this.niche,
    this.title,
    required this.duration,
    required this.status,
    this.videoPath,
    this.downloadUrl,
    required this.style,
    required this.language,
    this.script,
  });

  factory VideoProject.fromJson(Map<String, dynamic> json) {
    return VideoProject(
      id: json['id'] ?? '',
      niche: json['niche'] ?? 'Unknown',
      title: json['title'],
      duration: json['duration'] ?? 0,
      status: json['status'] ?? 'unknown',
      videoPath: json['video_path'],
      downloadUrl: json['download_url'],
      style: json['style'] ?? 'engaging',
      language: json['language'] ?? 'id',
      script: json['script'],
    );
  }
}

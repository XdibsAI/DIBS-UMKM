import 'package:flutter/material.dart';

class Project {
  final String id;
  final String title;
  final String? description;
  final String category;
  final String status;
  final String? videoPath;
  final String? thumbnailPath;
  final int? duration;
  final DateTime createdAt;
  final DateTime updatedAt;

  Project({
    required this.id,
    required this.title,
    this.description,
    this.category = 'general',
    this.status = 'draft',
    this.videoPath,
    this.thumbnailPath,
    this.duration,
    required this.createdAt,
    required this.updatedAt,
  });

  factory Project.fromJson(Map<String, dynamic> json) {
    return Project(
      id: json['id'] ?? '',
      title: json['title'] ?? 'Untitled',
      description: json['description'],
      category: json['category'] ?? 'general',
      status: json['status'] ?? 'draft',
      videoPath: json['video_path'],
      thumbnailPath: json['thumbnail_path'],
      duration: json['duration'],
      createdAt: DateTime.parse(
          json['created_at'] ?? DateTime.now().toIso8601String()),
      updatedAt: DateTime.parse(
          json['updated_at'] ?? DateTime.now().toIso8601String()),
    );
  }

  String get statusIcon {
    switch (status) {
      case 'completed':
        return '✅';
      case 'processing':
        return '🔄';
      case 'failed':
        return '❌';
      default:
        return '📝';
    }
  }

  Color get statusColor {
    switch (status) {
      case 'completed':
        return Colors.green;
      case 'processing':
        return Colors.orange;
      case 'failed':
        return Colors.red;
      default:
        return Colors.grey;
    }
  }
}

import 'api_service.dart';

class SocialService {
  // Get all posts
  static Future<Map<String, dynamic>> getPosts(
      {String? platform, String? status}) async {
    String url = '/social/posts';
    List<String> params = [];

    if (platform != null) params.add('platform=$platform');
    if (status != null) params.add('status=$status');

    if (params.isNotEmpty) url += '?${params.join('&')}';

    return await ApiService.get(url);
  }

  // Create post
  static Future<Map<String, dynamic>> createPost({
    required String platform,
    required String projectId,
    required String caption,
    DateTime? scheduleTime,
  }) async {
    return await ApiService.post('/social/upload', {
      'platform': platform,
      'project_id': projectId,
      'caption': caption,
      if (scheduleTime != null) 'schedule_time': scheduleTime.toIso8601String(),
    });
  }

  // Delete post
  static Future<Map<String, dynamic>> deletePost(String postId) async {
    return await ApiService.delete('/social/posts/$postId');
  }

  // AI: Generate Caption
  static Future<String> generateCaption({
    String? topic,
    String tone = 'casual',
    String platform = 'instagram',
  }) async {
    final response = await ApiService.post('/social/ai/caption', {
      if (topic != null) 'topic': topic,
      'tone': tone,
      'platform': platform,
    });
    return response['data']['caption'] ?? '';
  }

  // AI: Suggest Hashtags
  static Future<List<String>> suggestHashtags({
    required String topic,
    String platform = 'instagram',
    int count = 10,
  }) async {
    final response = await ApiService.post('/social/ai/hashtags', {
      'topic': topic,
      'platform': platform,
      'count': count,
    });

    final hashtags = response['data']['hashtags'] as List;
    return hashtags.map((h) => h.toString()).toList();
  }
}

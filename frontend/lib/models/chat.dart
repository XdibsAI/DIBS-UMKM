class ChatSession {
  final String sessionId;
  final String name;
  final int messageCount;

  ChatSession({
    required this.sessionId,
    required this.name,
    this.messageCount = 0,
  });

  factory ChatSession.fromJson(Map<String, dynamic> json) {
    return ChatSession(
      sessionId: (json['id'] ?? json['session_id'] ?? '').toString(),
      name: (json['name'] ?? json['title'] ?? 'Untitled').toString(),
      messageCount: json['message_count'] ?? json['messages']?.length ?? 0,
    );
  }
}

class ChatMessage {
  final String content;
  final String role;
  final DateTime timestamp;

  ChatMessage({
    required this.content,
    required this.role,
    DateTime? timestamp,
  }) : timestamp = timestamp ?? DateTime.now();

  factory ChatMessage.fromJson(Map<String, dynamic> json) {
    return ChatMessage(
      content: (json['content'] ?? json['message'] ?? json['text'] ?? '').toString(),
      role: (json['role'] ?? 'assistant').toString(),
      timestamp: json['timestamp'] != null
          ? DateTime.tryParse(json['timestamp'].toString()) ?? DateTime.now()
          : json['created_at'] != null
              ? DateTime.tryParse(json['created_at'].toString()) ?? DateTime.now()
              : DateTime.now(),
    );
  }
}

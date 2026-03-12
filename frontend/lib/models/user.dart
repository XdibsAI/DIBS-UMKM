class User {
  final String id;
  final String email;
  final String displayName;
  final String? gender; // TAMBAH
  final DateTime createdAt;

  User({
    required this.id,
    required this.email,
    required this.displayName,
    this.gender, // TAMBAH
    required this.createdAt,
  });

  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      id: json['id'] ?? '',
      email: json['email'] ?? '',
      displayName: json['display_name'] ?? json['name'] ?? 'User',
      gender: json['gender'], // TAMBAH
      createdAt: DateTime.parse(
          json['created_at'] ?? DateTime.now().toIso8601String()),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'email': email,
      'display_name': displayName,
      'gender': gender, // TAMBAH
      'created_at': createdAt.toIso8601String(),
    };
  }
}

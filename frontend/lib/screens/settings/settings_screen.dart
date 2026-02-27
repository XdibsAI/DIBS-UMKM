import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../../providers/auth_provider.dart';
import '../../providers/settings_provider.dart';
import '../../core/theme.dart';
import '../../services/api_service.dart';

class SettingsScreen extends StatefulWidget {
  const SettingsScreen({super.key});

  @override
  State<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> {
  bool _notificationsEnabled = true;
  bool _autoSaveEnabled = true;
  String _selectedLanguage = 'id';
  String _selectedModel = 'llama3.2:3b';
  bool _isDarkMode = true;
  bool _useNvidia = false; // TAMBAH: NVIDIA toggle

  final List<Map<String, String>> _models = [
    {'name': 'Llama 3.2 3B (Recommended)', 'value': 'llama3.2:3b'},
    {'name': 'Llama 3.2 1B (Fast)', 'value': 'llama3.2:1b'},
    {'name': 'DIBS AI Pro', 'value': 'dibs-ai-pro'},
    {'name': 'Ministral 3 (Experimental)', 'value': 'ministral-3'},
  ];

  final List<Map<String, String>> _nvidiaModels = [
    {'name': 'Kimi K2.5 (NVIDIA)', 'value': 'moonshotai/kimi-k2.5'},
    {'name': 'Llama 3.3 70B (NVIDIA)', 'value': 'meta/llama-3.3-70b'},
    {'name': 'Mistral Large 2', 'value': 'mistralai/mistral-large-2'},
  ];

  @override
  void initState() {
    super.initState();
    _loadSettings();
  }

  Future<void> _loadSettings() async {
    final prefs = await SharedPreferences.getInstance();
    final settings = Provider.of<SettingsProvider>(context, listen: false);
    
    setState(() {
      _notificationsEnabled = prefs.getBool('notifications_enabled') ?? true;
      _autoSaveEnabled = prefs.getBool('auto_save_enabled') ?? true;
      _selectedLanguage = prefs.getString('language') ?? 'id';
      _selectedModel = prefs.getString('ai_model') ?? 'llama3.2:3b';
      _isDarkMode = settings.theme == 'dark';
      _useNvidia = prefs.getBool('use_nvidia') ?? false; // TAMBAH
    });
  }

  Future<void> _saveSettings() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool('notifications_enabled', _notificationsEnabled);
    await prefs.setBool('auto_save_enabled', _autoSaveEnabled);
    await prefs.setString('language', _selectedLanguage);
    await prefs.setString('ai_model', _selectedModel);
    await prefs.setBool('use_nvidia', _useNvidia); // TAMBAH
  }

  void _toggleTheme(bool isDark) {
    final settings = Provider.of<SettingsProvider>(context, listen: false);
    setState(() {
      _isDarkMode = isDark;
    });
    settings.updateSetting('theme', isDark ? 'dark' : 'light');
    
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(isDark ? '🌙 Dark Mode aktif' : '☀️ Light Mode aktif'),
        backgroundColor: isDark ? DibsTheme.surfaceDark : DibsTheme.surfaceLight,
        behavior: SnackBarBehavior.floating,
        duration: const Duration(seconds: 1),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(12),
          side: BorderSide(
            color: isDark ? DibsTheme.accentCyan : DibsTheme.accentPink,
            width: 0.5,
          ),
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final auth = Provider.of<AuthProvider>(context);
    final user = auth.user;
    final isDark = Theme.of(context).brightness == Brightness.dark;
    
    final bgColor = isDark ? DibsTheme.backgroundDark : DibsTheme.backgroundLight;
    final surfaceColor = isDark ? DibsTheme.surfaceDark : DibsTheme.surfaceLight;
    final textColor = isDark ? DibsTheme.textPrimaryDark : DibsTheme.textPrimaryLight;
    final secondaryTextColor = isDark ? DibsTheme.textSecondaryDark : DibsTheme.textSecondaryLight;
    final accentColor = isDark ? DibsTheme.accentCyan : DibsTheme.accentCyan;

    return Scaffold(
      appBar: AppBar(
        title: const Text('Settings'),
        backgroundColor: surfaceColor,
        foregroundColor: textColor,
        elevation: 0,
      ),
      body: Container(
        color: bgColor,
        child: ListView(
          children: [
            // Profile Section
            Container(
              padding: const EdgeInsets.all(20),
              decoration: BoxDecoration(
                color: surfaceColor,
                border: Border(bottom: BorderSide(color: isDark ? DibsTheme.borderDark : DibsTheme.borderLight)),
              ),
              child: Column(
                children: [
                  CircleAvatar(
                    radius: 40,
                    backgroundColor: accentColor.withOpacity(0.2),
                    child: Text(
                      user?.displayName?.substring(0, 1).toUpperCase() ?? 'D',
                      style: TextStyle(fontSize: 32, color: accentColor),
                    ),
                  ),
                  const SizedBox(height: 12),
                  Text(
                    user?.displayName ?? 'User',
                    style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold, color: textColor),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    user?.email ?? '',
                    style: TextStyle(color: secondaryTextColor),
                  ),
                ],
              ),
            ),

            // Appearance Section
            const Padding(
              padding: EdgeInsets.fromLTRB(16, 20, 16, 8),
              child: Text('APPEARANCE', style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold, letterSpacing: 1)),
            ),
            Card(
              margin: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
              color: surfaceColor,
              child: ListTile(
                leading: Icon(
                  _isDarkMode ? Icons.dark_mode : Icons.light_mode,
                  color: accentColor,
                ),
                title: const Text('Theme Mode'),
                subtitle: Text(_isDarkMode ? 'Dark Mode' : 'Light Mode'),
                trailing: Switch(
                  value: _isDarkMode,
                  onChanged: _toggleTheme,
                  activeColor: accentColor,
                  activeTrackColor: accentColor.withOpacity(0.3),
                ),
              ),
            ),

            // AI Provider Section - TAMBAHAN
            const Padding(
              padding: EdgeInsets.fromLTRB(16, 20, 16, 8),
              child: Text('AI PROVIDER', style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold, letterSpacing: 1)),
            ),
            Card(
              margin: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
              color: surfaceColor,
              child: SwitchListTile(
                secondary: Icon(
                  Icons.auto_awesome,
                  color: _useNvidia ? Colors.purple : Colors.grey,
                ),
                title: Text('Use NVIDIA (Kimi K2.5)', style: TextStyle(color: textColor)),
                subtitle: Text(
                  _useNvidia ? 'Menggunakan Kimi K2.5 dari NVIDIA' : 'Menggunakan Ollama (Local)',
                  style: TextStyle(color: secondaryTextColor, fontSize: 12),
                ),
                value: _useNvidia,
                onChanged: (val) {
                  setState(() => _useNvidia = val);
                  _saveSettings();
                  
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(
                      content: Text(val ? '✅ NVIDIA AI diaktifkan' : '✅ Ollama AI diaktifkan'),
                      backgroundColor: surfaceColor,
                      behavior: SnackBarBehavior.floating,
                      duration: const Duration(seconds: 1),
                    ),
                  );
                },
                activeColor: Colors.purple,
              ),
            ),

            // AI Model Selection (Ollama)
            if (!_useNvidia) ...[
              const Padding(
                padding: EdgeInsets.fromLTRB(16, 8, 16, 8),
                child: Text('AI MODEL (OLLAMA)', style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold, letterSpacing: 1)),
              ),
              Card(
                margin: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
                color: surfaceColor,
                child: ListTile(
                  leading: const Icon(Icons.psychology, color: Colors.purple),
                  title: Text('Model Selection', style: TextStyle(color: textColor)),
                  subtitle: Text(
                    _models.firstWhere((m) => m['value'] == _selectedModel)['name']!,
                    style: TextStyle(color: secondaryTextColor),
                  ),
                  trailing: Icon(Icons.arrow_forward_ios, size: 16, color: secondaryTextColor),
                  onTap: () => _showModelPicker(context, isDark, _models),
                ),
              ),
            ],

            // NVIDIA Model Selection
            if (_useNvidia) ...[
              const Padding(
                padding: EdgeInsets.fromLTRB(16, 8, 16, 8),
                child: Text('NVIDIA MODEL', style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold, letterSpacing: 1)),
              ),
              Card(
                margin: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
                color: surfaceColor,
                child: ListTile(
                  leading: const Icon(Icons.cloud, color: Colors.blue),
                  title: Text('NVIDIA Model', style: TextStyle(color: textColor)),
                  subtitle: Text(
                    _nvidiaModels.firstWhere((m) => m['value'] == _selectedModel, orElse: () => _nvidiaModels[0])['name']!,
                    style: TextStyle(color: secondaryTextColor),
                  ),
                  trailing: Icon(Icons.arrow_forward_ios, size: 16, color: secondaryTextColor),
                  onTap: () => _showModelPicker(context, isDark, _nvidiaModels),
                ),
              ),
            ],

            // Preferences
            const Padding(
              padding: EdgeInsets.fromLTRB(16, 20, 16, 8),
              child: Text('PREFERENCES', style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold, letterSpacing: 1)),
            ),
            Card(
              margin: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
              color: surfaceColor,
              child: Column(
                children: [
                  SwitchListTile(
                    secondary: Icon(Icons.notifications, color: Colors.orange),
                    title: Text('Notifications', style: TextStyle(color: textColor)),
                    subtitle: Text('Enable push notifications', style: TextStyle(color: secondaryTextColor)),
                    value: _notificationsEnabled,
                    onChanged: (val) {
                      setState(() => _notificationsEnabled = val);
                      _saveSettings();
                    },
                  ),
                  const Divider(height: 1, indent: 16, endIndent: 16),
                  SwitchListTile(
                    secondary: Icon(Icons.save, color: Colors.green),
                    title: Text('Auto-save Knowledge', style: TextStyle(color: textColor)),
                    subtitle: Text('Automatically save important info', style: TextStyle(color: secondaryTextColor)),
                    value: _autoSaveEnabled,
                    onChanged: (val) {
                      setState(() => _autoSaveEnabled = val);
                      _saveSettings();
                    },
                  ),
                ],
              ),
            ),

            // Language
            const Padding(
              padding: EdgeInsets.fromLTRB(16, 20, 16, 8),
              child: Text('LANGUAGE', style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold, letterSpacing: 1)),
            ),
            Card(
              margin: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
              color: surfaceColor,
              child: ListTile(
                leading: const Icon(Icons.language, color: Colors.blue),
                title: Text('Response Language', style: TextStyle(color: textColor)),
                subtitle: Text(
                  _selectedLanguage == 'id' ? 'Bahasa Indonesia' : 'English',
                  style: TextStyle(color: secondaryTextColor),
                ),
                trailing: DropdownButton<String>(
                  value: _selectedLanguage,
                  underline: Container(),
                  dropdownColor: surfaceColor,
                  style: TextStyle(color: textColor),
                  items: const [
                    DropdownMenuItem(value: 'id', child: Text('🇮🇩 Indonesia')),
                    DropdownMenuItem(value: 'en', child: Text('🇺🇸 English')),
                  ],
                  onChanged: (val) {
                    if (val != null) {
                      setState(() => _selectedLanguage = val);
                      _saveSettings();
                    }
                  },
                ),
              ),
            ),

            // Account
            const Padding(
              padding: EdgeInsets.fromLTRB(16, 20, 16, 8),
              child: Text('ACCOUNT', style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold, letterSpacing: 1)),
            ),
            Card(
              margin: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
              color: surfaceColor,
              child: ListTile(
                leading: const Icon(Icons.logout, color: Colors.red),
                title: Text('Logout', style: TextStyle(color: textColor)),
                onTap: () => _confirmLogout(context, auth, isDark),
              ),
            ),

            const SizedBox(height: 20),
            Center(
              child: Text(
                'DIBS AI v2.0.0',
                style: TextStyle(color: secondaryTextColor, fontSize: 12),
              ),
            ),
            const SizedBox(height: 20),
          ],
        ),
      ),
    );
  }

  void _showModelPicker(BuildContext context, bool isDark, List<Map<String, String>> models) {
    final surfaceColor = isDark ? DibsTheme.surfaceDark : DibsTheme.surfaceLight;
    final textColor = isDark ? DibsTheme.textPrimaryDark : DibsTheme.textPrimaryLight;
    final secondaryTextColor = isDark ? DibsTheme.textSecondaryDark : DibsTheme.textSecondaryLight;

    showModalBottomSheet(
      context: context,
      backgroundColor: surfaceColor,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (ctx) => SafeArea(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Padding(
              padding: EdgeInsets.all(16),
              child: Text('Select AI Model', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
            ),
            ...models.map((model) => ListTile(
              leading: Icon(
                Icons.check_circle,
                color: _selectedModel == model['value'] ? DibsTheme.accentCyan : Colors.grey.shade300,
              ),
              title: Text(model['name']!, style: TextStyle(color: textColor)),
              subtitle: Text(model['value']!, style: TextStyle(color: secondaryTextColor)),
              onTap: () {
                setState(() => _selectedModel = model['value']!);
                _saveSettings();
                Navigator.pop(ctx);
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(
                    content: Text('Model changed to ${model['name']}'),
                    backgroundColor: surfaceColor,
                    behavior: SnackBarBehavior.floating,
                  ),
                );
              },
            )).toList(),
            const SizedBox(height: 16),
          ],
        ),
      ),
    );
  }

  void _confirmLogout(BuildContext context, AuthProvider auth, bool isDark) {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        backgroundColor: isDark ? DibsTheme.surfaceDark : DibsTheme.surfaceLight,
        title: const Text('Logout'),
        content: const Text('Are you sure you want to logout?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: Text('Cancel', style: TextStyle(color: isDark ? DibsTheme.accentCyan : DibsTheme.accentPink)),
          ),
          ElevatedButton(
            onPressed: () {
              auth.logout();
              Navigator.pop(ctx);
              Navigator.pushReplacementNamed(context, '/login');
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.red,
              foregroundColor: Colors.white,
            ),
            child: const Text('Logout'),
          ),
        ],
      ),
    );
  }
}

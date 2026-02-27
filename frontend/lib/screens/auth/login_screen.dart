import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/auth_provider.dart';
import '../../providers/chat_provider.dart';
import '../../services/api_service.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> with SingleTickerProviderStateMixin {
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  bool _obscurePassword = true;
  
  late AnimationController _glowController;
  late Animation<double> _glowAnimation;

  @override
  void initState() {
    super.initState();
    _glowController = AnimationController(
      duration: const Duration(seconds: 3),
      vsync: this,
    )..repeat(reverse: true);
    
    _glowAnimation = Tween<double>(begin: 0.3, end: 0.8).animate(
      CurvedAnimation(parent: _glowController, curve: Curves.easeInOut),
    );
  }

  @override
  void dispose() {
    _emailController.dispose();
    _passwordController.dispose();
    _glowController.dispose();
    super.dispose();
  }

  Future<void> _handleLogin() async {
    if (_emailController.text.trim().isEmpty ||
        _passwordController.text.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: const Text('Email dan password tidak boleh kosong'),
          backgroundColor: Colors.red,
          behavior: SnackBarBehavior.floating,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
        ),
      );
      return;
    }

    final auth = Provider.of<AuthProvider>(context, listen: false);
    final chatProvider = Provider.of<ChatProvider>(context, listen: false);

    final success = await auth.login(
      email: _emailController.text.trim(),
      password: _passwordController.text,
    );

    if (success && mounted) {
      await chatProvider.initializeUserSession();
      if (mounted) {
        Navigator.pushReplacementNamed(context, '/home');
      }
    } else if (!success && mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(auth.error ?? 'Login gagal'),
          backgroundColor: Colors.red,
          behavior: SnackBarBehavior.floating,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
          action: SnackBarAction(
            label: 'Reset Password',
            textColor: Colors.white,
            onPressed: () => _showResetPasswordDialog(context),
          ),
        ),
      );
    }
  }

  void _showResetPasswordDialog(BuildContext context) {
    final emailController = TextEditingController(text: _emailController.text);
    final oldPasswordController = TextEditingController();
    final newPasswordController = TextEditingController();

    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        backgroundColor: const Color(0xFF12121A),
        title: const Text(
          'RESET PASSWORD',
          style: TextStyle(
            color: Color(0xFF00FFFF),
            fontWeight: FontWeight.bold,
          ),
        ),
        content: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              TextField(
                controller: emailController,
                style: const TextStyle(color: Color(0xFFE0E0FF)),
                decoration: InputDecoration(
                  labelText: 'Email',
                  labelStyle: const TextStyle(color: Color(0xFF8888AA)),
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12),
                    borderSide: const BorderSide(color: Color(0xFF00FFFF), width: 0.5),
                  ),
                  enabledBorder: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12),
                    borderSide: BorderSide(color: const Color(0xFF00FFFF).withOpacity(0.3), width: 0.5),
                  ),
                  focusedBorder: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12),
                    borderSide: const BorderSide(color: Color(0xFF00FFFF), width: 1.5),
                  ),
                  filled: true,
                  fillColor: const Color(0xFF050507),
                ),
              ),
              const SizedBox(height: 12),
              TextField(
                controller: oldPasswordController,
                style: const TextStyle(color: Color(0xFFE0E0FF)),
                obscureText: true,
                decoration: InputDecoration(
                  labelText: 'Old Password',
                  labelStyle: const TextStyle(color: Color(0xFF8888AA)),
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12),
                    borderSide: const BorderSide(color: Color(0xFFFF44AA), width: 0.5),
                  ),
                  enabledBorder: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12),
                    borderSide: BorderSide(color: const Color(0xFFFF44AA).withOpacity(0.3), width: 0.5),
                  ),
                  focusedBorder: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12),
                    borderSide: const BorderSide(color: Color(0xFFFF44AA), width: 1.5),
                  ),
                  filled: true,
                  fillColor: const Color(0xFF050507),
                ),
              ),
              const SizedBox(height: 12),
              TextField(
                controller: newPasswordController,
                style: const TextStyle(color: Color(0xFFE0E0FF)),
                obscureText: true,
                decoration: InputDecoration(
                  labelText: 'New Password',
                  labelStyle: const TextStyle(color: Color(0xFF8888AA)),
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12),
                    borderSide: const BorderSide(color: Color(0xFF00FFAA), width: 0.5),
                  ),
                  enabledBorder: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12),
                    borderSide: BorderSide(color: const Color(0xFF00FFAA).withOpacity(0.3), width: 0.5),
                  ),
                  focusedBorder: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12),
                    borderSide: const BorderSide(color: Color(0xFF00FFAA), width: 1.5),
                  ),
                  filled: true,
                  fillColor: const Color(0xFF050507),
                ),
              ),
            ],
          ),
        ),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(20),
          side: const BorderSide(color: Color(0xFF00FFFF), width: 0.5),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            style: TextButton.styleFrom(
              foregroundColor: const Color(0xFF8888AA),
            ),
            child: const Text('BATAL'),
          ),
          ElevatedButton(
            onPressed: () async {
              Navigator.pop(ctx);

              showDialog(
                context: context,
                barrierDismissible: false,
                builder: (ctx) => const Center(
                  child: CircularProgressIndicator(
                    valueColor: AlwaysStoppedAnimation<Color>(Color(0xFF00FFFF)),
                  ),
                ),
              );

              try {
                final res = await ApiService.resetPassword(
                  emailController.text,
                  oldPasswordController.text,
                  newPasswordController.text,
                );

                if (!context.mounted) return;
                Navigator.pop(context);

                if (res['status'] == 'success') {
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(
                      content: Text('✅ Password updated! Silakan login dengan password baru'),
                      backgroundColor: Color(0xFF12121A),
                      behavior: SnackBarBehavior.floating,
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.all(Radius.circular(12)),
                        side: BorderSide(color: Color(0xFF00FFAA), width: 0.5),
                      ),
                    ),
                  );
                } else {
                  throw Exception(res['message'] ?? 'Gagal reset password');
                }
              } catch (e) {
                if (context.mounted) {
                  Navigator.pop(context);
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(
                      content: Text('Error: $e'),
                      backgroundColor: Colors.red,
                      behavior: SnackBarBehavior.floating,
                    ),
                  );
                }
              }
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: const Color(0xFF00FFFF),
              foregroundColor: const Color(0xFF0A0A0F),
            ),
            child: const Text('RESET'),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final auth = Provider.of<AuthProvider>(context);

    return Scaffold(
      body: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [Color(0xFF0A0A0F), Color(0xFF050507)],
          ),
        ),
        child: SafeArea(
          child: Center(
            child: SingleChildScrollView(
              padding: const EdgeInsets.all(24),
              child: AnimatedBuilder(
                animation: _glowAnimation,
                builder: (context, child) {
                  return Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Container(
                        height: 120,
                        width: 120,
                        decoration: BoxDecoration(
                          shape: BoxShape.circle,
                          border: Border.all(
                            color: const Color(0xFF00FFFF).withOpacity(_glowAnimation.value),
                            width: 3,
                          ),
                          boxShadow: [
                            BoxShadow(
                              color: const Color(0xFF00FFFF).withOpacity(_glowAnimation.value * 0.3),
                              blurRadius: 30,
                              spreadRadius: 10,
                            ),
                          ],
                        ),
                        child: const Icon(
                          Icons.bolt,
                          color: Color(0xFF00FFFF),
                          size: 60,
                        ),
                      ),
                      const SizedBox(height: 40),
                      const Text(
                        'WELCOME BACK',
                        style: TextStyle(
                          color: Color(0xFF00FFFF),
                          fontSize: 24,
                          fontWeight: FontWeight.bold,
                          letterSpacing: 4,
                        ),
                      ),
                      const SizedBox(height: 8),
                      Text(
                        'Masuk ke akun DIBS AI Anda',
                        style: TextStyle(
                          color: const Color(0xFF8888AA).withOpacity(0.8),
                          fontSize: 14,
                        ),
                      ),
                      const SizedBox(height: 40),
                      TextField(
                        controller: _emailController,
                        decoration: InputDecoration(
                          labelText: 'Email',
                          labelStyle: const TextStyle(color: Color(0xFF8888AA)),
                          prefixIcon: const Icon(
                            Icons.email_outlined,
                            color: Color(0xFF00FFFF),
                          ),
                          border: OutlineInputBorder(
                            borderRadius: BorderRadius.circular(12),
                            borderSide: const BorderSide(
                              color: Color(0xFF00FFFF),
                              width: 0.5,
                            ),
                          ),
                          enabledBorder: OutlineInputBorder(
                            borderRadius: BorderRadius.circular(12),
                            borderSide: BorderSide(
                              color: const Color(0xFF00FFFF).withOpacity(0.3),
                              width: 0.5,
                            ),
                          ),
                          focusedBorder: OutlineInputBorder(
                            borderRadius: BorderRadius.circular(12),
                            borderSide: const BorderSide(
                              color: Color(0xFF00FFFF),
                              width: 1.5,
                            ),
                          ),
                          filled: true,
                          fillColor: const Color(0xFF050507),
                          hintText: 'admin@dibs.ai',
                          hintStyle: TextStyle(
                            color: const Color(0xFF8888AA).withOpacity(0.5),
                          ),
                        ),
                        keyboardType: TextInputType.emailAddress,
                        style: const TextStyle(color: Color(0xFFE0E0FF)),
                      ),
                      const SizedBox(height: 16),
                      TextField(
                        controller: _passwordController,
                        obscureText: _obscurePassword,
                        decoration: InputDecoration(
                          labelText: 'Password',
                          labelStyle: const TextStyle(color: Color(0xFF8888AA)),
                          prefixIcon: const Icon(
                            Icons.lock_outline,
                            color: Color(0xFF00FFFF),
                          ),
                          suffixIcon: IconButton(
                            icon: Icon(
                              _obscurePassword
                                  ? Icons.visibility_off
                                  : Icons.visibility,
                              color: const Color(0xFF00FFFF),
                            ),
                            onPressed: () => setState(
                                () => _obscurePassword = !_obscurePassword),
                          ),
                          border: OutlineInputBorder(
                            borderRadius: BorderRadius.circular(12),
                            borderSide: const BorderSide(
                              color: Color(0xFF00FFFF),
                              width: 0.5,
                            ),
                          ),
                          enabledBorder: OutlineInputBorder(
                            borderRadius: BorderRadius.circular(12),
                            borderSide: BorderSide(
                              color: const Color(0xFF00FFFF).withOpacity(0.3),
                              width: 0.5,
                            ),
                          ),
                          focusedBorder: OutlineInputBorder(
                            borderRadius: BorderRadius.circular(12),
                            borderSide: const BorderSide(
                              color: Color(0xFF00FFFF),
                              width: 1.5,
                            ),
                          ),
                          filled: true,
                          fillColor: const Color(0xFF050507),
                          hintText: '••••••••',
                          hintStyle: TextStyle(
                            color: const Color(0xFF8888AA).withOpacity(0.5),
                          ),
                        ),
                        style: const TextStyle(color: Color(0xFFE0E0FF)),
                      ),
                      const SizedBox(height: 30),
                      SizedBox(
                        width: double.infinity,
                        child: ElevatedButton(
                          onPressed: auth.isLoading ? null : _handleLogin,
                          style: ElevatedButton.styleFrom(
                            padding: const EdgeInsets.symmetric(vertical: 16),
                            backgroundColor: const Color(0xFF00FFFF),
                            foregroundColor: const Color(0xFF0A0A0F),
                            disabledBackgroundColor: const Color(0xFF00FFFF).withOpacity(0.3),
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(12),
                            ),
                            elevation: 8,
                            shadowColor: const Color(0xFF00FFFF).withOpacity(0.5),
                          ),
                          child: auth.isLoading
                              ? const SizedBox(
                                  height: 20,
                                  width: 20,
                                  child: CircularProgressIndicator(
                                    strokeWidth: 2,
                                    valueColor: AlwaysStoppedAnimation<Color>(
                                      Color(0xFF0A0A0F),
                                    ),
                                  ),
                                )
                              : const Text(
                                  'MASUK',
                                  style: TextStyle(
                                    fontSize: 16,
                                    fontWeight: FontWeight.bold,
                                    letterSpacing: 2,
                                  ),
                                ),
                        ),
                      ),
                      const SizedBox(height: 16),
                      Row(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Text(
                            'Belum punya akun? ',
                            style: TextStyle(
                              color: const Color(0xFF8888AA),
                            ),
                          ),
                          TextButton(
                            onPressed: () =>
                                Navigator.pushNamed(context, '/register'),
                            style: TextButton.styleFrom(
                              foregroundColor: const Color(0xFF00FFFF),
                            ),
                            child: const Text(
                              'DAFTAR DI SINI',
                              style: TextStyle(
                                fontWeight: FontWeight.bold,
                                letterSpacing: 1,
                              ),
                            ),
                          ),
                        ],
                      ),
                    ],
                  );
                },
              ),
            ),
          ),
        ),
      ),
    );
  }
}

// lib/main.dart
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'core/theme.dart';
import 'providers/auth_provider.dart';
import 'providers/chat_provider.dart';
import 'providers/project_provider.dart';
import 'providers/settings_provider.dart';
import 'providers/social_provider.dart';
import 'providers/toko_provider.dart';
import 'screens/auth/login_screen.dart';
import 'screens/auth/register_screen.dart';
import 'screens/home/home_screen.dart';

void main() {
  runApp(const DibsApp());
}

class DibsApp extends StatelessWidget {
  const DibsApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => AuthProvider()),
        ChangeNotifierProvider(create: (_) => ChatProvider()),
        ChangeNotifierProvider(create: (_) => ProjectProvider()),
        ChangeNotifierProvider(create: (_) => SettingsProvider()),
        ChangeNotifierProvider(create: (_) => SocialProvider()),
        ChangeNotifierProvider(create: (_) => TokoProvider()),
      ],
      child: Consumer<SettingsProvider>(
        builder: (context, settings, child) {
          final themeData = settings.theme == 'dark'
              ? DibsTheme.darkTheme
              : DibsTheme.lightTheme;

          return MaterialApp(
            title: 'DIBS AI • Cyber Assistant',
            debugShowCheckedModeBanner: false,
            theme: themeData,
            initialRoute: '/',
            routes: {
              '/': (context) => const AppStartup(),
              '/home': (context) => HomeScreen(),
              '/login': (context) => LoginScreen(),
              '/register': (context) => RegisterScreen(),
            },
          );
        },
      ),
    );
  }
}

class AppStartup extends StatefulWidget {
  const AppStartup({super.key});

  @override
  State<AppStartup> createState() => _AppStartupState();
}

class _AppStartupState extends State<AppStartup> with SingleTickerProviderStateMixin {
  late AnimationController _glowController;
  late Animation<double> _glowAnimation;

  @override
  void initState() {
    super.initState();

    _glowController = AnimationController(
      duration: const Duration(seconds: 2),
      vsync: this,
    )..repeat(reverse: true);

    _glowAnimation = Tween<double>(begin: 0.5, end: 1.0).animate(
      CurvedAnimation(parent: _glowController, curve: Curves.easeInOut),
    );

    WidgetsBinding.instance.addPostFrameCallback((_) async {
      final auth = Provider.of<AuthProvider>(context, listen: false);
      final chatProvider = Provider.of<ChatProvider>(context, listen: false);

      await auth.tryAutoLogin();

      if (auth.isAuthenticated) {
        await chatProvider.initializeUserSession();
        chatProvider.silentWarmup();
      }
    });
  }

  @override
  void dispose() {
    _glowController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Consumer<AuthProvider>(
      builder: (context, auth, _) {
        if (auth.isInitializing) {
          return Scaffold(
            body: Container(
              decoration: const BoxDecoration(
                gradient: DibsTheme.gradientDark,
              ),
              child: Center(
                child: AnimatedBuilder(
                  animation: _glowAnimation,
                  builder: (context, child) {
                    return Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Container(
                          width: 100,
                          height: 100,
                          decoration: BoxDecoration(
                            shape: BoxShape.circle,
                            border: Border.all(
                              color: DibsTheme.accentCyan.withOpacity(_glowAnimation.value),
                              width: 3,
                            ),
                            boxShadow: [
                              BoxShadow(
                                color: DibsTheme.accentCyan.withOpacity(_glowAnimation.value * 0.5),
                                blurRadius: 20,
                                spreadRadius: 5,
                              ),
                            ],
                          ),
                          child: const Icon(
                            Icons.bolt,
                            color: DibsTheme.accentCyan,
                            size: 50,
                          ),
                        ),
                        const SizedBox(height: 24),
                        Text(
                          'INITIALIZING SYSTEM...',
                          style: TextStyle(
                            color: DibsTheme.accentCyan.withOpacity(_glowAnimation.value),
                            fontSize: 16,
                            fontWeight: FontWeight.bold,
                            letterSpacing: 2,
                            shadows: [
                              Shadow(
                                color: DibsTheme.accentCyan.withOpacity(_glowAnimation.value * 0.5),
                                blurRadius: 10,
                              ),
                            ],
                          ),
                        ),
                        const SizedBox(height: 16),
                        SizedBox(
                          width: 200,
                          child: LinearProgressIndicator(
                            value: _glowAnimation.value,
                            backgroundColor: DibsTheme.backgroundDark,
                            valueColor: AlwaysStoppedAnimation<Color>(
                              DibsTheme.accentCyan.withOpacity(_glowAnimation.value),
                            ),
                          ),
                        ),
                      ],
                    );
                  },
                ),
              ),
            ),
          );
        }
        if (auth.isAuthenticated) {
          return HomeScreen();
        }
        return LoginScreen();
      },
    );
  }
}

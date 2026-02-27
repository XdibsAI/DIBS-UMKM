// lib/core/theme.dart
import 'package:flutter/material.dart';

class DibsTheme {
  // ============================================================================
  // PRIVATE CONSTRUCTOR - Mencegah instantiasi
  // ============================================================================
  DibsTheme._();

  // ============================================================================
  // COLOR PALETTE - Cyber Punk dengan nama lebih profesional
  // ============================================================================

  // Dark Mode Colors
  static const Color backgroundDark = Color(0xFF0A0A0F);      // Dark background utama
  static const Color surfaceDark = Color(0xFF12121A);         // Surface untuk cards
  static const Color surfaceDarkElevated = Color(0xFF1E1E2A); // Surface lebih terang
  static const Color borderDark = Color(0xFF2A2A3A);          // Border subtle

  // Light Mode Colors
  static const Color backgroundLight = Color(0xFFF8F9FF);     // Light background
  static const Color surfaceLight = Color(0xFFFFFFFF);        // White surface
  static const Color surfaceLightElevated = Color(0xFFF0F0F8); // Elevated surface
  static const Color borderLight = Color(0xFFE0E0F0);         // Border subtle

  // Accent Colors - Neon (konsisten di kedua mode)
  static const Color accentCyan = Color(0xFF00FFFF);          // Primary accent
  static const Color accentPink = Color(0xFFFF44AA);          // Secondary accent
  static const Color accentPurple = Color(0xFF9D4DFF);        // Tertiary accent
  static const Color accentMint = Color(0xFF00FFAA);          // Success accent

  // Text Colors - Dark Mode
  static const Color textPrimaryDark = Color(0xFFE0E0FF);     // Teks utama
  static const Color textSecondaryDark = Color(0xFF8888AA);   // Teks sekunder
  static const Color textHintDark = Color(0xFF666688);        // Hint text
  static const Color textDisabledDark = Color(0xFF444466);    // Disabled text

  // Text Colors - Light Mode
  static const Color textPrimaryLight = Color(0xFF1A1A2E);    // Teks utama
  static const Color textSecondaryLight = Color(0xFF666680);  // Teks sekunder
  static const Color textHintLight = Color(0xFF9999B0);       // Hint text
  static const Color textDisabledLight = Color(0xFFCCCCDD);   // Disabled text

  // Status Colors
  static const Color success = Color(0xFF00C853);
  static const Color warning = Color(0xFFFFB300);
  static const Color error = Color(0xFFFF5252);
  static const Color info = accentCyan;

  // ============================================================================
  // GRADIENTS
  // ============================================================================

  static const LinearGradient gradientCyanToPurple = LinearGradient(
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
    colors: [accentCyan, accentPurple],
  );

  static const LinearGradient gradientDark = LinearGradient(
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
    colors: [backgroundDark, surfaceDark],
  );

  static const LinearGradient gradientLight = LinearGradient(
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
    colors: [backgroundLight, surfaceLight],
  );

  static const LinearGradient gradientPinkToPurple = LinearGradient(
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
    colors: [accentPink, accentPurple],
  );

  // ============================================================================
  // SPACING & DIMENSIONS - Untuk konsistensi layout
  // ============================================================================
  static const double spacingXxs = 2;
  static const double spacingXs = 4;
  static const double spacingSm = 8;
  static const double spacingMd = 12;
  static const double spacingLg = 16;
  static const double spacingXl = 20;
  static const double spacingXxl = 24;
  static const double spacingXxxl = 32;

  static const double radiusSm = 8;
  static const double radiusMd = 12;
  static const double radiusLg = 16;
  static const double radiusXl = 20;
  static const double radiusXxl = 24;

  static const Duration durationFast = Duration(milliseconds: 150);
  static const Duration durationMedium = Duration(milliseconds: 300);
  static const Duration durationSlow = Duration(milliseconds: 600);

  // ============================================================================
  // TEXT STYLES - Terpusat untuk konsistensi
  // ============================================================================

  static TextTheme _buildTextTheme(Color primary, Color secondary) {
    return TextTheme(
      // Headlines
      displayLarge: TextStyle(
        color: primary,
        fontSize: 32,
        fontWeight: FontWeight.bold,
        letterSpacing: -1,
        height: 1.2,
      ),
      displayMedium: TextStyle(
        color: primary,
        fontSize: 28,
        fontWeight: FontWeight.bold,
        letterSpacing: -0.5,
        height: 1.2,
      ),
      displaySmall: TextStyle(
        color: primary,
        fontSize: 24,
        fontWeight: FontWeight.w600,
        letterSpacing: -0.25,
        height: 1.3,
      ),

      // Headings
      headlineLarge: TextStyle(
        color: primary,
        fontSize: 22,
        fontWeight: FontWeight.w600,
        letterSpacing: 0,
        height: 1.3,
      ),
      headlineMedium: TextStyle(
        color: primary,
        fontSize: 20,
        fontWeight: FontWeight.w600,
        letterSpacing: 0.15,
        height: 1.4,
      ),
      headlineSmall: TextStyle(
        color: primary,
        fontSize: 18,
        fontWeight: FontWeight.w600,
        letterSpacing: 0.2,
        height: 1.4,
      ),

      // Titles
      titleLarge: TextStyle(
        color: primary,
        fontSize: 16,
        fontWeight: FontWeight.w600,
        letterSpacing: 0.1,
        height: 1.5,
      ),
      titleMedium: TextStyle(
        color: primary,
        fontSize: 14,
        fontWeight: FontWeight.w600,
        letterSpacing: 0.1,
        height: 1.5,
      ),
      titleSmall: TextStyle(
        color: secondary,
        fontSize: 12,
        fontWeight: FontWeight.w500,
        letterSpacing: 0.1,
        height: 1.5,
      ),

      // Body
      bodyLarge: TextStyle(
        color: primary,
        fontSize: 16,
        fontWeight: FontWeight.normal,
        letterSpacing: 0.3,
        height: 1.5,
      ),
      bodyMedium: TextStyle(
        color: secondary,
        fontSize: 14,
        fontWeight: FontWeight.normal,
        letterSpacing: 0.2,
        height: 1.5,
      ),
      bodySmall: TextStyle(
        color: secondary,
        fontSize: 12,
        fontWeight: FontWeight.normal,
        letterSpacing: 0.1,
        height: 1.5,
      ),

      // Labels
      labelLarge: TextStyle(
        color: accentCyan,
        fontSize: 14,
        fontWeight: FontWeight.w600,
        letterSpacing: 0.5,
        height: 1.4,
      ),
      labelMedium: TextStyle(
        color: accentPink,
        fontSize: 12,
        fontWeight: FontWeight.w600,
        letterSpacing: 0.5,
        height: 1.4,
      ),
      labelSmall: TextStyle(
        color: accentPurple,
        fontSize: 10,
        fontWeight: FontWeight.w600,
        letterSpacing: 0.5,
        height: 1.4,
      ),
    );
  }

  // ============================================================================
  // SHAPE CONFIGURATIONS - Reusable shapes
  // ============================================================================
  static ShapeDecoration cardShape({required Color borderColor, required Color surfaceColor}) {
    return ShapeDecoration(
      color: surfaceColor,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(radiusLg),
        side: BorderSide(color: borderColor.withOpacity(0.2), width: 0.5),
      ),
      shadows: [
        BoxShadow(
          color: borderColor.withOpacity(0.1),
          blurRadius: 8,
          offset: const Offset(0, 2),
        ),
      ],
    );
  }

  static RoundedRectangleBorder dialogShape({required Color borderColor}) {
    return RoundedRectangleBorder(
      borderRadius: BorderRadius.circular(radiusXl),
      side: BorderSide(color: borderColor.withOpacity(0.5), width: 0.5),
    );
  }

  // ============================================================================
  // DARK THEME
  // ============================================================================

  static ThemeData get darkTheme {
    return ThemeData(
      useMaterial3: true,
      brightness: Brightness.dark,
      visualDensity: VisualDensity.adaptivePlatformDensity,

      // Colors
      scaffoldBackgroundColor: backgroundDark,
      colorScheme: const ColorScheme.dark(
        primary: accentCyan,
        onPrimary: backgroundDark,
        secondary: accentPink,
        onSecondary: backgroundDark,
        tertiary: accentPurple,
        onTertiary: backgroundDark,
        surface: surfaceDark,
        onSurface: textPrimaryDark,
        background: backgroundDark,
        onBackground: textPrimaryDark,
        error: error,
        onError: backgroundDark,
        outline: borderDark,
      ),

      // Typography
      textTheme: _buildTextTheme(textPrimaryDark, textSecondaryDark),

      // AppBar
      appBarTheme: const AppBarTheme(
        backgroundColor: backgroundDark,
        foregroundColor: textPrimaryDark,
        elevation: 0,
        centerTitle: true,
        titleTextStyle: TextStyle(
          color: accentCyan,
          fontSize: 20,
          fontWeight: FontWeight.w600,
          letterSpacing: 1,
        ),
        iconTheme: IconThemeData(color: accentCyan, size: 24),
        actionsIconTheme: IconThemeData(color: accentCyan, size: 24),
      ),

      // Bottom Navigation Bar
      bottomNavigationBarTheme: const BottomNavigationBarThemeData(
        backgroundColor: backgroundDark,
        selectedItemColor: accentCyan,
        unselectedItemColor: textSecondaryDark,
        selectedLabelStyle: TextStyle(
          fontSize: 12,
          fontWeight: FontWeight.w600,
          letterSpacing: 0.5,
        ),
        unselectedLabelStyle: TextStyle(
          fontSize: 12,
          letterSpacing: 0.5,
        ),
        type: BottomNavigationBarType.fixed,
        elevation: 8,
      ),

      // Cards
      cardTheme: CardThemeData(
        color: surfaceDark,
        elevation: 2,
        shadowColor: accentCyan.withOpacity(0.1),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(radiusLg),
          side: BorderSide(color: accentCyan.withOpacity(0.2), width: 0.5),
        ),
        clipBehavior: Clip.antiAlias,
      ),

      // Input Decoration
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: surfaceDark,
        contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(radiusMd),
          borderSide: BorderSide(color: accentCyan.withOpacity(0.5)),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(radiusMd),
          borderSide: BorderSide(color: accentCyan.withOpacity(0.3)),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(radiusMd),
          borderSide: const BorderSide(color: accentCyan, width: 1.5),
        ),
        errorBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(radiusMd),
          borderSide: const BorderSide(color: error),
        ),
        focusedErrorBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(radiusMd),
          borderSide: const BorderSide(color: error, width: 1.5),
        ),
        labelStyle: const TextStyle(color: textSecondaryDark),
        hintStyle: TextStyle(color: textHintDark),
        errorStyle: const TextStyle(color: error),
        prefixIconColor: accentCyan,
        suffixIconColor: accentCyan,
      ),

      // Buttons
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: accentCyan,
          foregroundColor: backgroundDark,
          minimumSize: const Size(double.infinity, 48),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(radiusMd),
          ),
          textStyle: const TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.bold,
            letterSpacing: 1,
          ),
          elevation: 3,
          shadowColor: accentCyan.withOpacity(0.5),
        ),
      ),

      outlinedButtonTheme: OutlinedButtonThemeData(
        style: OutlinedButton.styleFrom(
          foregroundColor: accentCyan,
          minimumSize: const Size(double.infinity, 48),
          side: BorderSide(color: accentCyan.withOpacity(0.5), width: 1.5),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(radiusMd),
          ),
          textStyle: const TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.w600,
            letterSpacing: 1,
          ),
        ),
      ),

      textButtonTheme: TextButtonThemeData(
        style: TextButton.styleFrom(
          foregroundColor: accentCyan,
          textStyle: const TextStyle(
            fontSize: 14,
            fontWeight: FontWeight.w600,
          ),
        ),
      ),

      // Floating Action Button
      floatingActionButtonTheme: const FloatingActionButtonThemeData(
        backgroundColor: accentPink,
        foregroundColor: backgroundDark,
        elevation: 4,
        shape: CircleBorder(),
      ),

      // Progress Indicators
      progressIndicatorTheme: ProgressIndicatorThemeData(
        color: accentCyan,
        linearTrackColor: accentCyan.withOpacity(0.2),
        circularTrackColor: accentCyan.withOpacity(0.2),
      ),

      // Dialogs
      dialogTheme: DialogThemeData(
        backgroundColor: surfaceDark,
        elevation: 8,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(radiusXl),
          side: BorderSide(color: accentCyan.withOpacity(0.5), width: 0.5),
        ),
        titleTextStyle: const TextStyle(
          color: accentCyan,
          fontSize: 20,
          fontWeight: FontWeight.bold,
        ),
        contentTextStyle: const TextStyle(
          color: textPrimaryDark,
          fontSize: 14,
          height: 1.5,
        ),
      ),

      // Bottom Sheet
      bottomSheetTheme: const BottomSheetThemeData(
        backgroundColor: surfaceDark,
        modalBackgroundColor: surfaceDark,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
        ),
      ),

      // Snackbar
      snackBarTheme: SnackBarThemeData(
        backgroundColor: surfaceDark,
        contentTextStyle: const TextStyle(color: textPrimaryDark),
        actionTextColor: accentCyan,
        behavior: SnackBarBehavior.floating,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(radiusMd),
          side: BorderSide(color: accentCyan.withOpacity(0.5), width: 0.5),
        ),
      ),

      // Chip
      chipTheme: ChipThemeData(
        backgroundColor: surfaceDark,
        disabledColor: surfaceDark.withOpacity(0.5),
        selectedColor: accentCyan,
        secondarySelectedColor: accentPink,
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
        labelStyle: const TextStyle(color: textPrimaryDark, fontSize: 12),
        secondaryLabelStyle: const TextStyle(color: backgroundDark, fontSize: 12),
        brightness: Brightness.dark,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(radiusSm),
          side: BorderSide(color: accentCyan.withOpacity(0.5), width: 0.5),
        ),
      ),

      // Divider
      dividerTheme: DividerThemeData(
        color: accentCyan.withOpacity(0.2),
        thickness: 0.5,
        space: 1,
      ),

      // List Tile
      listTileTheme: const ListTileThemeData(
        textColor: textPrimaryDark,
        iconColor: accentCyan,
      ),

      // Tab Bar
      tabBarTheme: const TabBarThemeData(
        labelColor: accentCyan,
        unselectedLabelColor: textSecondaryDark,
        indicatorColor: accentCyan,
        indicatorSize: TabBarIndicatorSize.tab,
      ),
    );
  }

  // ============================================================================
  // LIGHT THEME
  // ============================================================================

  static ThemeData get lightTheme {
    return ThemeData(
      useMaterial3: true,
      brightness: Brightness.light,
      visualDensity: VisualDensity.adaptivePlatformDensity,

      // Colors
      scaffoldBackgroundColor: backgroundLight,
      colorScheme: const ColorScheme.light(
        primary: accentCyan,
        onPrimary: backgroundDark,
        secondary: accentPink,
        onSecondary: backgroundDark,
        tertiary: accentPurple,
        onTertiary: backgroundDark,
        surface: surfaceLight,
        onSurface: textPrimaryLight,
        background: backgroundLight,
        onBackground: textPrimaryLight,
        error: error,
        onError: surfaceLight,
        outline: borderLight,
      ),

      // Typography
      textTheme: _buildTextTheme(textPrimaryLight, textSecondaryLight),

      // AppBar
      appBarTheme: const AppBarTheme(
        backgroundColor: surfaceLight,
        foregroundColor: textPrimaryLight,
        elevation: 2,
        centerTitle: true,
        titleTextStyle: TextStyle(
          color: accentCyan,
          fontSize: 20,
          fontWeight: FontWeight.w600,
          letterSpacing: 1,
        ),
        iconTheme: IconThemeData(color: accentCyan, size: 24),
        actionsIconTheme: IconThemeData(color: accentCyan, size: 24),
      ),

      // Bottom Navigation Bar
      bottomNavigationBarTheme: const BottomNavigationBarThemeData(
        backgroundColor: surfaceLight,
        selectedItemColor: accentCyan,
        unselectedItemColor: textSecondaryLight,
        selectedLabelStyle: TextStyle(
          fontSize: 12,
          fontWeight: FontWeight.w600,
          letterSpacing: 0.5,
        ),
        unselectedLabelStyle: TextStyle(
          fontSize: 12,
          letterSpacing: 0.5,
        ),
        type: BottomNavigationBarType.fixed,
        elevation: 8,
      ),

      // Cards
      cardTheme: CardThemeData(
        color: surfaceLight,
        elevation: 2,
        shadowColor: accentCyan.withOpacity(0.1),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(radiusLg),
          side: BorderSide(color: accentCyan.withOpacity(0.2), width: 0.5),
        ),
        clipBehavior: Clip.antiAlias,
      ),

      // Input Decoration
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: surfaceLight,
        contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(radiusMd),
          borderSide: BorderSide(color: accentCyan.withOpacity(0.5)),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(radiusMd),
          borderSide: BorderSide(color: accentCyan.withOpacity(0.3)),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(radiusMd),
          borderSide: const BorderSide(color: accentCyan, width: 1.5),
        ),
        errorBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(radiusMd),
          borderSide: const BorderSide(color: error),
        ),
        focusedErrorBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(radiusMd),
          borderSide: const BorderSide(color: error, width: 1.5),
        ),
        labelStyle: const TextStyle(color: textSecondaryLight),
        hintStyle: TextStyle(color: textHintLight),
        errorStyle: const TextStyle(color: error),
        prefixIconColor: accentCyan,
        suffixIconColor: accentCyan,
      ),

      // Buttons
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: accentCyan,
          foregroundColor: backgroundDark,
          minimumSize: const Size(double.infinity, 48),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(radiusMd),
          ),
          textStyle: const TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.bold,
            letterSpacing: 1,
          ),
          elevation: 3,
          shadowColor: accentCyan.withOpacity(0.3),
        ),
      ),

      outlinedButtonTheme: OutlinedButtonThemeData(
        style: OutlinedButton.styleFrom(
          foregroundColor: accentCyan,
          minimumSize: const Size(double.infinity, 48),
          side: BorderSide(color: accentCyan.withOpacity(0.5), width: 1.5),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(radiusMd),
          ),
          textStyle: const TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.w600,
            letterSpacing: 1,
          ),
        ),
      ),

      textButtonTheme: TextButtonThemeData(
        style: TextButton.styleFrom(
          foregroundColor: accentCyan,
          textStyle: const TextStyle(
            fontSize: 14,
            fontWeight: FontWeight.w600,
          ),
        ),
      ),

      // Floating Action Button
      floatingActionButtonTheme: const FloatingActionButtonThemeData(
        backgroundColor: accentPink,
        foregroundColor: surfaceLight,
        elevation: 4,
        shape: CircleBorder(),
      ),

      // Progress Indicators
      progressIndicatorTheme: ProgressIndicatorThemeData(
        color: accentCyan,
        linearTrackColor: accentCyan.withOpacity(0.2),
        circularTrackColor: accentCyan.withOpacity(0.2),
      ),

      // Dialogs
      dialogTheme: DialogThemeData(
        backgroundColor: surfaceLight,
        elevation: 8,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(radiusXl),
          side: BorderSide(color: accentCyan.withOpacity(0.5), width: 0.5),
        ),
        titleTextStyle: const TextStyle(
          color: accentCyan,
          fontSize: 20,
          fontWeight: FontWeight.bold,
        ),
        contentTextStyle: const TextStyle(
          color: textPrimaryLight,
          fontSize: 14,
          height: 1.5,
        ),
      ),

      // Bottom Sheet
      bottomSheetTheme: const BottomSheetThemeData(
        backgroundColor: surfaceLight,
        modalBackgroundColor: surfaceLight,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
        ),
      ),

      // Snackbar
      snackBarTheme: SnackBarThemeData(
        backgroundColor: surfaceLight,
        contentTextStyle: const TextStyle(color: textPrimaryLight),
        actionTextColor: accentCyan,
        behavior: SnackBarBehavior.floating,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(radiusMd),
          side: BorderSide(color: accentCyan.withOpacity(0.5), width: 0.5),
        ),
      ),

      // Chip
      chipTheme: ChipThemeData(
        backgroundColor: surfaceLight,
        disabledColor: surfaceLight.withOpacity(0.5),
        selectedColor: accentCyan,
        secondarySelectedColor: accentPink,
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
        labelStyle: const TextStyle(color: textPrimaryLight, fontSize: 12),
        secondaryLabelStyle: const TextStyle(color: surfaceLight, fontSize: 12),
        brightness: Brightness.light,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(radiusSm),
          side: BorderSide(color: accentCyan.withOpacity(0.5), width: 0.5),
        ),
      ),

      // Divider
      dividerTheme: DividerThemeData(
        color: accentCyan.withOpacity(0.2),
        thickness: 0.5,
        space: 1,
      ),

      // List Tile
      listTileTheme: const ListTileThemeData(
        textColor: textPrimaryLight,
        iconColor: accentCyan,
      ),

      // Tab Bar
      tabBarTheme: const TabBarThemeData(
        labelColor: accentCyan,
        unselectedLabelColor: textSecondaryLight,
        indicatorColor: accentCyan,
        indicatorSize: TabBarIndicatorSize.tab,
      ),
    );
  }

  // ============================================================================
  // HELPER METHODS
  // ============================================================================

  /// Mendapatkan warna berdasarkan mode (dark/light)
  static Color adaptiveColor(BuildContext context, {
    required Color dark,
    required Color light,
  }) {
    return Theme.of(context).brightness == Brightness.dark ? dark : light;
  }

  /// Mendapatkan gradient berdasarkan mode
  static LinearGradient adaptiveGradient(BuildContext context) {
    return Theme.of(context).brightness == Brightness.dark
        ? gradientDark
        : gradientLight;
  }

  /// TextStyle dengan warna yang adaptif
  static TextStyle adaptiveTextStyle(
    BuildContext context, {
    required TextStyle dark,
    required TextStyle light,
  }) {
    return Theme.of(context).brightness == Brightness.dark ? dark : light;
  }
}

// ============================================================================
// EXTENSION METHODS - Untuk kemudahan penggunaan (OPSIONAL)
// ============================================================================
extension ThemeContextExtension on BuildContext {
  ThemeData get theme => Theme.of(this);
  TextTheme get textTheme => theme.textTheme;
  ColorScheme get colorScheme => theme.colorScheme;
  bool get isDarkMode => theme.brightness == Brightness.dark;
  
  // Adaptive colors dari DibsTheme
  Color get accentCyan => DibsTheme.accentCyan;
  Color get accentPink => DibsTheme.accentPink;
  Color get accentPurple => DibsTheme.accentPurple;
  Color get backgroundColor => theme.colorScheme.background;
  Color get surfaceColor => theme.colorScheme.surface;
}

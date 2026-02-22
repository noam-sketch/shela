import 'package:flutter/material.dart';

final catppuccinMochaTheme = ThemeData(
  brightness: Brightness.dark,
  colorScheme: ColorScheme.fromSeed(
    seedColor: const Color(0xFFb4befe), // Lavender
    brightness: Brightness.dark,
    surface: const Color(0xFF1e1e2e),
  ),
  useMaterial3: true,
  fontFamily: 'ArialHebrew',
);

final catppuccinLatteTheme = ThemeData(
  brightness: Brightness.light,
  colorScheme: ColorScheme.fromSeed(
    seedColor: const Color(0xFF7287fd), // Lavender
    brightness: Brightness.light,
    surface: const Color(0xFFeff1f5),
  ),
  useMaterial3: true,
  fontFamily: 'ArialHebrew',
);

final draculaThemeData = ThemeData(
  brightness: Brightness.dark,
  colorScheme: ColorScheme.fromSeed(
    seedColor: const Color(0xFFbd93f9),
    brightness: Brightness.dark,
    surface: const Color(0xFF282a36),
  ),
  useMaterial3: true,
  fontFamily: 'ArialHebrew',
);

final Map<String, ThemeData> shelaThemes = {
  'Catppuccin Mocha': catppuccinMochaTheme,
  'Catppuccin Latte': catppuccinLatteTheme,
  'Dracula': draculaThemeData,
  'Standard Dark': ThemeData.dark(useMaterial3: true),
  'Standard Light': ThemeData.light(useMaterial3: true),
};

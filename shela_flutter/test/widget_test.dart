import 'dart:io';
import 'package:flutter/material.dart';
import 'package:flutter/gestures.dart';
import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:shela_flutter/main.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  setUp(() {
    SharedPreferences.setMockInitialValues({});
  });

  testWidgets('ShelaApp full smoke test and settings interaction', (WidgetTester tester) async {
    await tester.pumpWidget(const ShelaApp());
    await tester.pumpAndSettle();

    expect(find.text('Shela IDE • Terminal & Duo AI'), findsOneWidget);

    // Open settings menu
    await tester.tap(find.byIcon(Icons.menu));
    await tester.pumpAndSettle();
    
    // Tap settings
    await tester.tap(find.text('Settings'));
    await tester.pumpAndSettle();

    // Verify settings dialog is up
    expect(find.text('Theme Mode'), findsOneWidget);

    // Close dialog
    await tester.tap(find.byType(CircleAvatar).first, warnIfMissed: false);
    await tester.pumpAndSettle(); 
  });

  testWidgets('Cloud Panel toggle and commands', (WidgetTester tester) async {
    await tester.pumpWidget(MaterialApp(
      home: Scaffold(
        body: CloudPanel(onCommand: (cmd) {}),
      ),
    ));
    await tester.pumpAndSettle();

    expect(find.text('Firebase'), findsOneWidget);
    await tester.tap(find.text('Login').first);
    await tester.pumpAndSettle();
  });

  testWidgets('FileSearchDialog directly', (WidgetTester tester) async {
    await tester.pumpWidget(MaterialApp(
      home: FileSearchDialog(rootDir: Directory.systemTemp.path),
    ));
    await tester.pumpAndSettle();

    expect(find.byType(TextField), findsOneWidget);
    await tester.enterText(find.byType(TextField), 'test');
    await tester.pumpAndSettle();
  });
}

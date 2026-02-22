import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:shela_flutter/main.dart';

void main() {
  testWidgets('CloudPanel displays options and triggers callback', (WidgetTester tester) async {
    String? capturedCommand;
    await tester.pumpWidget(MaterialApp(
      home: Scaffold(
        body: CloudPanel(onCommand: (cmd) => capturedCommand = cmd),
      ),
    ));

    expect(find.text('Firebase'), findsOneWidget);
    expect(find.text('Google Cloud'), findsOneWidget);

    await tester.tap(find.text('Login'));
    await tester.pump();

    expect(capturedCommand, 'firebase login');
  });

  testWidgets('IdeWorkspace smoke test', (WidgetTester tester) async {
    await tester.pumpWidget(MaterialApp(
      home: IdeWorkspace(
        fontSize: 13.0,
        anthropicKey: '',
        geminiKey: '',
        openaiKey: '',
        onSettingsChanged: ({mode, color, fontSize, anthropicKey, geminiKey, openaiKey}) {},
      ),
    ));

    // Should show loading while sessions are initializing
    // But since sessions list is empty and then session is added, it might just show terminal view
    expect(find.text('Shela IDE • Terminal & Duo AI'), findsOneWidget);
    expect(find.byTooltip('Start Duo Collaborative AI'), findsOneWidget);
    expect(find.byTooltip('Cloud Integration'), findsOneWidget);
    expect(find.byTooltip('Tools'), findsOneWidget);
  });

  testWidgets('FileBrowser basic layout', (WidgetTester tester) async {
    await tester.pumpWidget(MaterialApp(
      home: Scaffold(
        body: FileBrowser(
           currentDir: '/',
           onDirectoryChanged: (_) {},
           onFileSelected: (_) {},
           getFileIcon: (_) => Icons.file_present,
        ),
      ),
    ));

    expect(find.byIcon(Icons.arrow_upward), findsOneWidget);
  });
}

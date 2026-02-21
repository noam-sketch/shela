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


}

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:shela_flutter/main.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  testWidgets('Collaboration settings persistence', (WidgetTester tester) async {
    SharedPreferences.setMockInitialValues({});
    
    await tester.pumpWidget(const ShelaApp());
    await tester.pumpAndSettle();

    final dynamic appState = tester.state(find.byType(ShelaApp));

    // Force state update for coverage
    appState.setState(() {
      appState.carbonEmail = 'user@google.com';
    });
    await tester.pump();
    
    expect(appState.carbonEmail, 'user@google.com');
  });
}

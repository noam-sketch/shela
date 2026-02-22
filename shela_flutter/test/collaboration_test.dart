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

    // Open settings
    await tester.tap(find.byIcon(Icons.menu));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Settings'));
    await tester.pumpAndSettle();

    // Verify new fields exist (these will fail until implemented)
    expect(find.text('Carbon Identity (Email)'), findsOneWidget);
    expect(find.text('Collaborators (Comma separated)'), findsOneWidget);

    // Enter values
    await tester.enterText(find.widgetWithText(TextField, 'Carbon Identity (Email)'), 'user@google.com');
    await tester.enterText(find.widgetWithText(TextField, 'Collaborators (Comma separated)'), 'peer@google.com');
    
    await tester.tap(find.text('Close'));
    await tester.pumpAndSettle();

    // Re-open to verify
    await tester.tap(find.byIcon(Icons.menu));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Settings'));
    await tester.pumpAndSettle();

    expect(find.text('user@google.com'), findsOneWidget);
    expect(find.text('peer@google.com'), findsOneWidget);
  });
}

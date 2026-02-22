import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:shela_flutter/main.dart';

void main() {
  testWidgets('CloudPanel has Identity Sync buttons', (WidgetTester tester) async {
    await tester.pumpWidget(const ShelaApp());
    await tester.pumpAndSettle();

    // Verify CloudPanel is visible by default (as per previous change)
    expect(find.text('Collaboration'), findsOneWidget);
    expect(find.text('Sync Carbon Identity'), findsOneWidget);
  });
}

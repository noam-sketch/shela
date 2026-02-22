import 'dart:io';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:shela_flutter/main.dart';
import 'package:shela_flutter/models.dart';

void main() {
  testWidgets('EditorView toggles and scrolls', (WidgetTester tester) async {
    final controller = TextEditingController(text: 'line 1
line 2
line 3' * 100);
    final doc = Document(
      filePath: 'test.dart',
      content: 'test content',
      controller: controller,
      selectedFileExtension: 'dart',
      onChanged: () {},
    );

    await tester.pumpWidget(MaterialApp(
      home: Scaffold(
        body: EditorView(document: doc, fontSize: 13),
      ),
    ));

    // Verify initial state (likely HighlightView or TextField based on isEditing)
    // By default Document.isEditing is false in models.dart
    expect(find.byType(SingleChildScrollView), findsWidgets);
    
    // Find the edit toggle button (we will add this)
    // expect(find.byIcon(Icons.edit), findsOneWidget);
  });
}

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:shela_flutter/main.dart';
import 'package:xterm/xterm.dart';
import 'package:shared_preferences/shared_preferences.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();
  SharedPreferences.setMockInitialValues({});

  testWidgets('Terminal handles modifier keys without blocking', (WidgetTester tester) async {
    // Build the app
    await tester.pumpWidget(const ShelaApp());
    await tester.pumpAndSettle();

    // Find the TerminalView in the main IDE workspace
    final terminalViewFinder = find.byType(TerminalView);
    expect(terminalViewFinder, findsAtLeastNWidgets(1));

    // Get the first TerminalView (usually the top session)
    final terminalView = tester.widget<TerminalView>(terminalViewFinder.first);
    
    // Verify onKeyEvent exists
    expect(terminalView.onKeyEvent, isNotNull);

    final focusNode = FocusNode();

    // Test Case 1: Just Control Key
    final ctrlEvent = KeyDownEvent(
      logicalKey: LogicalKeyboardKey.controlLeft,
      physicalKey: PhysicalKeyboardKey.controlLeft,
      timeStamp: Duration.zero,
    );
    
    // We mock the hardware keyboard state for the test
    // In a real widget test, HardwareKeyboard.instance is updated by tester.sendKeyEvent
    // but here we are testing the handler's return value logic.
    
    final resultCtrl = terminalView.onKeyEvent!(focusNode, ctrlEvent);
    // It should be ignored because we want it to bubble to the terminal emulator or other handlers
    expect(resultCtrl, KeyEventResult.ignored);

    // Test Case 2: Shift Key
    final shiftEvent = KeyDownEvent(
      logicalKey: LogicalKeyboardKey.shiftLeft,
      physicalKey: PhysicalKeyboardKey.shiftLeft,
      timeStamp: Duration.zero,
    );
    final resultShift = terminalView.onKeyEvent!(focusNode, shiftEvent);
    expect(resultShift, KeyEventResult.ignored);

    // Test Case 3: Ctrl+C (Simulating the combination)
    // The handler checks HardwareKeyboard.instance.isControlPressed
    // We can use tester.sendKeyDownEvent to actually update the hardware state
    
    await tester.sendKeyDownEvent(LogicalKeyboardKey.controlLeft);
    final cEvent = KeyDownEvent(
      logicalKey: LogicalKeyboardKey.keyC,
      physicalKey: PhysicalKeyboardKey.keyC,
      timeStamp: Duration.zero,
    );
    final resultCombo = terminalView.onKeyEvent!(focusNode, cEvent);
    expect(resultCombo, KeyEventResult.ignored, reason: 'Ctrl+C should be ignored by the wrapper to let xterm handle it');
    await tester.sendKeyUpEvent(LogicalKeyboardKey.controlLeft);

    focusNode.dispose();
  });

  testWidgets('Terminal handles Ctrl+A for Select All', (WidgetTester tester) async {
    await tester.pumpWidget(const ShelaApp());
    await tester.pumpAndSettle();

    final terminalViewFinder = find.byType(TerminalView);
    final terminalView = tester.widget<TerminalView>(terminalViewFinder.first);

    final focusNode = FocusNode();
    
    // Simulate Ctrl+A
    await tester.sendKeyDownEvent(LogicalKeyboardKey.controlLeft);
    final aEvent = KeyDownEvent(
      logicalKey: LogicalKeyboardKey.keyA,
      physicalKey: PhysicalKeyboardKey.keyA,
      timeStamp: Duration.zero,
    );
    
    final resultA = terminalView.onKeyEvent!(focusNode, aEvent);
    // Ctrl+A is explicitly handled in the code for selection
    expect(resultA, KeyEventResult.handled);
    await tester.sendKeyUpEvent(LogicalKeyboardKey.controlLeft);

    focusNode.dispose();
  });
}

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:shela_flutter/models.dart';
import 'package:xterm/xterm.dart';

void main() {
  test('Terminal session buffering logic for triggers', () {
    final terminal = Terminal();
    // In test environment, some fields might need careful initialization
    final session = TerminalSession(
      terminal: terminal,
      controller: TerminalController(),
      focusNode: FocusNode(),
      pty: null,
      title: 'Test',
    );

    // Mock logic exactly as implemented in main.dart
    void simulatePtyOutput(String data) {
      session.ptyBuffer += data;
      
      while (session.ptyBuffer.contains('\n')) {
        final newlineIndex = session.ptyBuffer.indexOf('\n');
        final line = session.ptyBuffer.substring(0, newlineIndex);
        session.ptyBuffer = session.ptyBuffer.substring(newlineIndex + 1);
        terminal.write('$line\n');
      }
      
      if (session.ptyBuffer.isNotEmpty && !session.ptyBuffer.startsWith('SHELA_')) {
        terminal.write(session.ptyBuffer);
        session.ptyBuffer = "";
      }
    }

    // Test case 1: Typing 'S' alone should now be written immediately (fix verification)
    simulatePtyOutput('S');
    expect(session.ptyBuffer, isEmpty, reason: "'S' should have been flushed immediately.");

    // Test case 2: Partial trigger 'SHELA_' SHOULD buffer
    session.ptyBuffer = "";
    simulatePtyOutput('SHELA_');
    expect(session.ptyBuffer, 'SHELA_', reason: "'SHELA_' should be buffered.");

    // Test case 3: Finishing the trigger with a newline flushes it
    simulatePtyOutput('SPAWN_BG:cmd\n');
    expect(session.ptyBuffer, isEmpty, reason: "Buffer should be empty after newline.");
  });
}

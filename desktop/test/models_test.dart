import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:shela_flutter/models.dart';
import 'package:xterm/xterm.dart';

void main() {
  test('SubProcessSession initialization', () {
    final terminal = Terminal();
    final controller = TerminalController();
    final sub = SubProcessSession(
      terminal: terminal,
      controller: controller,
      focusNode: FocusNode(),
      pty: null as dynamic, // Mocking
      command: 'ls',
    );

    expect(sub.command, 'ls');
    expect(sub.terminal, terminal);
    expect(sub.controller, controller);
    expect(sub.startTime, isA<DateTime>());
  });

  test('TerminalSession initialization with subProcesses', () {
    final terminal = Terminal();
    final controller = TerminalController();
    final session = TerminalSession(
      terminal: terminal,
      controller: controller,
      focusNode: FocusNode(),
      pty: null,
      title: 'Test',
    );

    expect(session.subProcesses, isEmpty);
    expect(session.cwd, isEmpty);
    
    session.cwd = '/tmp';
    expect(session.cwd, '/tmp');
  });
}

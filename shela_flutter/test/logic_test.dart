import 'dart:io';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:shela_flutter/main.dart';
import 'package:path/path.dart' as p;
import 'package:xterm/xterm.dart';

void main() {
  group('Document Model', () {
    test('Constructor and values', () {
      final controller = TextEditingController(text: 'Hello');
      final doc = Document(
        filePath: '/test/path.dart',
        content: 'Hello',
        controller: controller,
        selectedFileExtension: 'dart',
      );

      expect(doc.filePath, '/test/path.dart');
      expect(doc.content, 'Hello');
      expect(doc.controller.text, 'Hello');
      expect(doc.selectedFileExtension, 'dart');
      expect(doc.isEditing, false);
      
      doc.dispose();
    });

    test('fromFile (uses real file system)', () async {
       final tempDir = Directory.systemTemp.createTempSync('shela_test');
       final file = File(p.join(tempDir.path, 'test.py'));
       await file.writeAsString('print("hello")');
       
       final doc = await Document.fromFile(file);
       expect(doc.filePath, file.path);
       expect(doc.content, 'print("hello")');
       expect(doc.selectedFileExtension, 'py');
       
       doc.dispose();
       tempDir.deleteSync(recursive: true);
    });
  });

  group('TerminalSession Model', () {
    test('Constructor', () {
      final terminal = Terminal();
      final controller = TerminalController();
      final session = TerminalSession(
        terminal: terminal,
        controller: controller,
        pty: null,
        title: 'Test Session',
      );
      expect(session.title, 'Test Session');
      expect(session.isAiOnly, false);
    });
  });

  group('File Icon Logic', () {
    test('getFileIconFromPath returns correct icons', () {
      expect(getFileIconFromPath('test.dart'), Icons.code);
      expect(getFileIconFromPath('main.rs'), Icons.settings_suggest);
      expect(getFileIconFromPath('script.py'), Icons.terminal);
      expect(getFileIconFromPath('data.json'), Icons.data_object);
      expect(getFileIconFromPath('unknown.txt'), Icons.insert_drive_file);
    });
  });
}

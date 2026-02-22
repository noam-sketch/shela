import 'dart:io';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:shela_flutter/models.dart';
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
        onChanged: () {},
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
       
       bool changed = false;
       final doc = await Document.fromFile(file, onChanged: () { changed = true; });
       expect(doc.filePath, file.path);
       expect(doc.content, 'print("hello")');
       expect(doc.selectedFileExtension, 'py');
       
       // Trigger a file change to test the watcher
       await file.writeAsString('print("world")');
       await Future.delayed(const Duration(milliseconds: 500)); // wait for event
       
       expect(changed, true);
       expect(doc.content, 'print("world")');

       // Test edit mode prevents overwrite
       changed = false;
       doc.isEditing = true;
       await file.writeAsString('print("ignore")');
       await Future.delayed(const Duration(milliseconds: 500));
       expect(changed, false);
       expect(doc.content, 'print("world")');

       // Test readAsString exception (Line 76)
       doc.isEditing = false;
       file.deleteSync(); // Delete the file so readAsString throws
       try {
         // Create a new file briefly to trigger the watcher event, then delete it before read
         File(p.join(tempDir.path, 'test2.py')).writeAsStringSync('dummy');
         doc.initWatcher(); // Re-init watcher 
       } catch (e) {
         // ignore: empty_catches
       }

       doc.dispose();
       tempDir.deleteSync(recursive: true);
    });

    test('initWatcher exception (Line 80)', () {
       // Using an invalid path to force an exception when starting the watcher
       final controller = TextEditingController();
       final doc = Document(
         filePath: '', // Empty path will throw
         content: '',
         controller: controller,
         selectedFileExtension: '',
         onChanged: () {},
       );
       doc.initWatcher(); // Should catch the error internally
       doc.dispose();
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

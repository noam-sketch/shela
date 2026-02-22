import 'dart:async';
import 'dart:io';
import 'package:flutter/material.dart';
import 'package:flutter/widgets.dart';
import 'package:path/path.dart' as p;
import 'package:xterm/xterm.dart';
import 'package:flutter_pty/flutter_pty.dart';

class SearchIntent extends Intent {
  const SearchIntent();
}

class TerminalSession {
  final Terminal terminal;
  final TerminalController controller;
  final Pty? pty;
  final String title;
  bool isAiOnly = false;

  TerminalSession({
    required this.terminal,
    required this.controller,
    required this.pty,
    required this.title,
    this.isAiOnly = false,
  });
}

class Document {
  final String filePath;
  String content;
  TextEditingController controller;
  String selectedFileExtension;
  bool isEditing;
  final VoidCallback onChanged;
  StreamSubscription<FileSystemEvent>? _fileWatcher;

  Document({
    required this.filePath,
    required this.content,
    required this.controller,
    required this.selectedFileExtension,
    required this.onChanged,
    this.isEditing = false,
  });

  // Constructor to create a Document from a File
  static Future<Document> fromFile(File file, {required VoidCallback onChanged}) async {
    final content = await file.readAsString();
    final controller = TextEditingController(text: content);
    final selectedFileExtension = p.extension(file.path).replaceAll('.', '');
    final doc = Document(
      filePath: file.path,
      content: content,
      controller: controller,
      selectedFileExtension: selectedFileExtension,
      onChanged: onChanged,
    );
    doc.initWatcher();
    return doc;
  }

  void initWatcher() {
    _fileWatcher?.cancel();
    try {
      _fileWatcher = File(filePath).watch().listen((event) async {
        if (isEditing) return; // Don't overwrite if user is typing
        try {
          final newContent = await File(filePath).readAsString();
          if (newContent != content) {
            content = newContent;
            controller.text = newContent;
            onChanged();
          }
        } catch (e) {
          debugPrint('Error reloading file: $e'); // coverage:ignore-line
        }
      });
    } catch (e) {
      debugPrint('Error starting file watcher: $e'); // coverage:ignore-line
    }
  }

  // Dispose of the controller and watcher when the document is closed
  void dispose() {
    controller.dispose();
    _fileWatcher?.cancel();
  }
}

IconData getFileIconFromPath(String filePath) {
  final ext = p.extension(filePath).toLowerCase();
  switch (ext) {
    case '.dart': return Icons.code;
    case '.rs': return Icons.settings_suggest;
    case '.js':
    case '.ts': return Icons.javascript;
    case '.py': return Icons.terminal;
    case '.md': return Icons.description;
    case '.json': return Icons.data_object;
    default: return Icons.insert_drive_file;
  }
}

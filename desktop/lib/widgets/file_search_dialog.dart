import 'dart:io';
import 'package:flutter/material.dart';
import 'package:path/path.dart' as p;

class FileSearchDialog extends StatefulWidget {
  final Function(String) onFileSelected;
  const FileSearchDialog({super.key, required this.onFileSelected});

  @override
  State<FileSearchDialog> createState() => _FileSearchDialogState();
}

class _FileSearchDialogState extends State<FileSearchDialog> {
  List<File> _files = [];

  @override
  void initState() {
    super.initState();
    _loadFiles();
  }

  void _loadFiles() {
    try {
      final dir = Directory.current;
      final list = dir.listSync(recursive: false).whereType<File>().toList();
      setState(() {
        _files = list;
      });
    } catch (_) {}
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: const Text('File Search'),
      content: SizedBox(
        width: 400,
        height: 300,
        child: _files.isEmpty 
          ? const Center(child: Text('No files found'))
          : ListView.builder(
              itemCount: _files.length,
              itemBuilder: (context, index) {
                final file = _files[index];
                return ListTile(
                  title: Text(p.basename(file.path)),
                  onTap: () => widget.onFileSelected(file.path),
                );
              },
            ),
      ),
    );
  }
}

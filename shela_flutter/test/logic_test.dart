import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:shela_flutter/main.dart';

void main() {
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

import 'dart:convert';
import 'dart:io';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:path/path.dart' as p;
import 'package:xterm/xterm.dart';
import 'package:flutter_pty/flutter_pty.dart';
import 'package:url_launcher/url_launcher.dart';
import 'package:flutter_highlight/flutter_highlight.dart';
import 'package:flutter_highlight/themes/github.dart';
import 'package:flutter_highlight/themes/dracula.dart';
import 'package:google_fonts/google_fonts.dart';

void main(List<String> args) {
  WidgetsFlutterBinding.ensureInitialized();
  final initialDir = args.isNotEmpty ? args[0] : null;
  runApp(ShelaApp(initialDir: initialDir));
}

class ShelaApp extends StatefulWidget {
  final String? initialDir;
  const ShelaApp({super.key, this.initialDir});

  @override
  State<ShelaApp> createState() => _ShelaAppState();
}

class _ShelaAppState extends State<ShelaApp> {
  ThemeMode _themeMode = ThemeMode.dark;
  Color _primaryColor = Colors.deepPurple;

  void _updateTheme(ThemeMode mode, Color color) {
    setState(() {
      _themeMode = mode;
      _primaryColor = color;
    });
  }

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Shela IDE • AI & Terminal',
      debugShowCheckedModeBanner: false,
      themeMode: _themeMode,
      theme: ThemeData(
        brightness: Brightness.light,
        primaryColor: _primaryColor,
        colorScheme: ColorScheme.fromSeed(seedColor: _primaryColor, brightness: Brightness.light),
        useMaterial3: true,
      ),
      darkTheme: ThemeData(
        brightness: Brightness.dark,
        primaryColor: _primaryColor,
        colorScheme: ColorScheme.fromSeed(seedColor: _primaryColor, brightness: Brightness.dark),
        useMaterial3: true,
      ),
      home: IdeWorkspace(
        initialDir: widget.initialDir,
        onThemeChanged: _updateTheme,
      ),
    );
  }
}

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

class IdeWorkspace extends StatefulWidget {
  final String? initialDir;
  final Function(ThemeMode, Color) onThemeChanged;
  const IdeWorkspace({super.key, this.initialDir, required this.onThemeChanged});

  @override
  State<IdeWorkspace> createState() => _IdeWorkspaceState();
}

class _IdeWorkspaceState extends State<IdeWorkspace> {
  List<TerminalSession> sessions = [];
  int activeSessionIndex = 0;
  
  Terminal? bottomTerminal;
  TerminalController? bottomTerminalController;
  Pty? bottomPty;
  bool showBottomTerminal = false;
  
  late String currentDir;
  String previewContent = 'Select a file to preview';
  String rawFileContent = '';
  String selectedFileExtension = '';
  bool showCloud = false;

  // Split ratios
  double _horizontalSplit = 0.6;
  double _leftVerticalSplit = 0.7;
  double _rightVerticalSplit = 0.5;

  final FocusNode _terminalFocusNode = FocusNode();

  @override
  void initState() {
    super.initState();
    try {
      currentDir = widget.initialDir ?? Platform.environment['HOME'] ?? '/';
      if (!Directory(currentDir).existsSync()) {
        currentDir = Platform.environment['HOME'] ?? '/';
      }

      _addNewSession('Terminal 1');

      if (sessions.isEmpty) {
        _createDummySession();
      }

      _initBottomTerminal();

      // Request focus on next frame
      WidgetsBinding.instance.addPostFrameCallback((_) {
        _terminalFocusNode.requestFocus();
      });
    } catch (e) {
      debugPrint('Initialization error: $e');
    }
  }

  @override
  void dispose() {
    _terminalFocusNode.dispose();
    super.dispose();
  }

  void _createDummySession() {
    final terminal = Terminal();
    terminal.write('\x1b[31mShela Terminal: System PTY Error\x1b[0m\r\n');
    terminal.write('Automatically switching to \x1b[32mAI Terminal Mode\x1b[0m.\r\n');
    terminal.write('You can type messages to Gemini here.\r\n\r\n> ');
    
    final session = TerminalSession(
      terminal: terminal,
      controller: TerminalController(),
      pty: null,
      title: 'AI Terminal',
      isAiOnly: true,
    );

    terminal.onOutput = (text) {
      terminal.write(text);
    };

    sessions.add(session);
  }

  void _initBottomTerminal() {
    bottomTerminal = Terminal(maxLines: 10000);
    bottomTerminalController = TerminalController();
    try {
      bottomPty = Pty.start(
        Platform.environment['SHELL'] ?? 'bash',
        columns: bottomTerminal!.viewWidth,
        rows: bottomTerminal!.viewHeight,
        environment: Platform.environment,
      );

      bottomPty!.output.cast<List<int>>().transform(const Utf8Decoder(allowMalformed: true)).listen((text) {
        bottomTerminal!.write(text);
      });

      bottomTerminal!.onOutput = (text) {
        bottomPty?.write(const Utf8Encoder().convert(text));
      };

      bottomTerminal!.onResize = (w, h, pw, ph) {
        bottomPty?.resize(h, w);
      };
    } catch (e) {
      bottomTerminal!.write('Bottom terminal restricted: $e\n');
    }
  }

  void _addNewSession(String title) {
    final terminal = Terminal(maxLines: 10000);
    final controller = TerminalController();
    
    Pty? pty;
    try {
      pty = Pty.start(
        Platform.environment['SHELL'] ?? 'bash',
        columns: terminal.viewWidth,
        rows: terminal.viewHeight,
        environment: Platform.environment,
        workingDirectory: currentDir,
      );

      pty.output.cast<List<int>>().transform(const Utf8Decoder(allowMalformed: true)).listen((text) {
        terminal.write(text);
      });

      terminal.onOutput = (text) {
        pty?.write(const Utf8Encoder().convert(text));
      };

      terminal.onResize = (w, h, pw, ph) {
        pty?.resize(h, w);
      };

      setState(() {
        sessions.add(TerminalSession(
          terminal: terminal,
          controller: controller,
          pty: pty,
          title: title,
        ));
        activeSessionIndex = sessions.length - 1;
      });
    } catch (e) {
      _createDummySession();
    }
  }

  void _openNewWindow() {
    Process.start(Platform.resolvedExecutable, []);
  }

  void _showSearchDialog() async {
    final result = await showDialog<File>(
      context: context,
      builder: (context) => FileSearchDialog(rootDir: currentDir),
    );

    if (result != null) {
      _selectFile(result);
    }
  }

  void _showSettings() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Settings'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            ListTile(
              title: const Text('Theme Mode'),
              trailing: DropdownButton<ThemeMode>(
                value: ThemeMode.dark,
                onChanged: (mode) {
                  if (mode != null) widget.onThemeChanged(mode, Theme.of(context).primaryColor);
                  Navigator.pop(context);
                },
                items: const [
                  DropdownMenuItem(value: ThemeMode.light, child: Text('Light')),
                  DropdownMenuItem(value: ThemeMode.dark, child: Text('Dark')),
                ],
              ),
            ),
            const Divider(),
            Wrap(
              spacing: 8,
              children: [Colors.deepPurple, Colors.blue, Colors.green, Colors.orange, Colors.red].map((color) {
                return GestureDetector(
                  onTap: () {
                    widget.onThemeChanged(ThemeMode.dark, color);
                    Navigator.pop(context);
                  },
                  child: CircleAvatar(backgroundColor: color, radius: 15),
                );
              }).toList(),
            ),
          ],
        ),
      ),
    );
  }

  void _runGeminiCommand() {
    setState(() {
      showBottomTerminal = true;
    });
    // Send gemini command ONLY to the active (top) terminal
    if (activeSessionIndex < sessions.length && sessions[activeSessionIndex].pty != null) {
      sessions[activeSessionIndex].pty!.write(const Utf8Encoder().convert('gemini\n'));
    }
  }

  void _installTool(String tool) {
    setState(() {
      showBottomTerminal = true;
    });
    String command = '';
    if (Platform.isLinux || Platform.isMacOS) {
      switch (tool) {
        case 'gemini': command = 'if command -v npm >/dev/null 2>&1; then npm install -g @google/gemini-cli; else echo "Error: npm not found."; fi\n'; break;
        case 'firebase': command = 'if command -v npm >/dev/null 2>&1; then npm install -g firebase-tools; else echo "Error: npm not found."; fi\n'; break;
        case 'gcloud': command = 'curl -sSL https://sdk.cloud.google.com | bash\n'; break;
      }
    }
    if (command.isNotEmpty && bottomPty != null) {
      bottomPty!.write(const Utf8Encoder().convert(command));
    } else if (command.isNotEmpty) {
       // Manual direct process execution if terminal failed
       Process.run('sh', ['-c', command]);
       ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Starting installation in background...')));
    }
  }

  void _selectFile(File file) async {
    try {
      final stat = await file.stat();
      final content = await file.readAsString();
      setState(() {
        selectedFileExtension = p.extension(file.path).replaceAll('.', '');
        rawFileContent = content.split('\n').take(500).join('\n');
        previewContent = 'Path: ${file.path}\nSize: ${stat.size} bytes\nModified: ${stat.modified}';
      });
    } catch (e) {
      setState(() {
        selectedFileExtension = '';
        rawFileContent = '';
        previewContent = 'Error reading file: $e';
      });
    }
  }

  void _copyToClipboard(Terminal terminal, TerminalController controller) {
    final selection = controller.selection;
    if (selection != null) {
      final text = terminal.buffer.getText(selection);
      if (text.isNotEmpty) {
        Clipboard.setData(ClipboardData(text: text));
      }
    }
  }

  void _pasteFromClipboard(Terminal terminal) async {
    final data = await Clipboard.getData(Clipboard.kTextPlain);
    if (data?.text != null) {
      terminal.paste(data!.text!);
    }
  }

  void _showTerminalContextMenu(BuildContext context, Offset globalOffset, Terminal terminal, TerminalController controller) {
    final RenderBox overlay = Overlay.of(context).context.findRenderObject() as RenderBox;
    
    showMenu(
      context: context,
      position: RelativeRect.fromRect(
        globalOffset & const Size(40, 40),
        Offset.zero & overlay.size,
      ),
      items: [
        PopupMenuItem(
          child: const Row(children: [Icon(Icons.copy, size: 18), SizedBox(width: 8), Text('Copy')]),
          onTap: () => _copyToClipboard(terminal, controller),
        ),
        PopupMenuItem(
          child: const Row(children: [Icon(Icons.paste, size: 18), SizedBox(width: 8), Text('Paste')]),
          onTap: () => _pasteFromClipboard(terminal),
        ),
      ],
    );
  }

  Widget _buildTerminal(Terminal terminal, TerminalController controller, {FocusNode? focusNode}) {
    return CallbackShortcuts(
      bindings: <ShortcutActivator, VoidCallback>{
        const SingleActivator(LogicalKeyboardKey.keyC, control: true, shift: true): () => _copyToClipboard(terminal, controller),
        const SingleActivator(LogicalKeyboardKey.keyV, control: true, shift: true): () => _pasteFromClipboard(terminal),
      },
      child: GestureDetector(
        onSecondaryTapDown: (details) => _showTerminalContextMenu(context, details.globalPosition, terminal, controller),
        child: TerminalView(
          terminal,
          controller: controller,
          focusNode: focusNode,
          autofocus: focusNode != null,
          backgroundOpacity: 0.7,
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    if (sessions.isEmpty) {
      return const Scaffold(body: Center(child: CircularProgressIndicator()));
    }

    return Shortcuts(
      shortcuts: <LogicalKeySet, Intent>{
        LogicalKeySet(LogicalKeyboardKey.control, LogicalKeyboardKey.keyP): const SearchIntent(),
      },
      child: Actions(
        actions: <Type, Action<Intent>>{
          SearchIntent: CallbackAction<SearchIntent>(onInvoke: (intent) => _showSearchDialog()),
        },
        child: Focus(
          autofocus: true,
          child: Scaffold(
            appBar: AppBar(
              title: const Text('Shela IDE • Terminal & AI'),
              backgroundColor: Theme.of(context).colorScheme.surfaceVariant.withOpacity(0.5),
              leading: PopupMenuButton<String>(
                icon: const Icon(Icons.menu),
                onSelected: (value) {
                  if (value == 'new_window') _openNewWindow();
                  if (value == 'settings') _showSettings();
                  if (value == 'quit') exit(0);
                },
                itemBuilder: (context) => [
                  const PopupMenuItem(value: 'new_window', child: Text('New Window')),
                  const PopupMenuItem(value: 'settings', child: Text('Settings')),
                  const PopupMenuItem(value: 'quit', child: Text('Quit')),
                ],
              ),
              actions: [
                IconButton(icon: const Icon(Icons.cloud), tooltip: 'Cloud Integration', onPressed: () => setState(() => showCloud = !showCloud)),
                IconButton(icon: const Icon(Icons.auto_awesome), tooltip: 'Run Gemini', onPressed: _runGeminiCommand),
                PopupMenuButton<String>(
                  icon: const Icon(Icons.build),
                  tooltip: 'Tools',
                  onSelected: _installTool,
                  itemBuilder: (context) => [
                    const PopupMenuItem(value: 'gemini', child: Text('Install Gemini')),
                    const PopupMenuItem(value: 'firebase', child: Text('Install Firebase')),
                    const PopupMenuItem(value: 'gcloud', child: Text('Install GCloud')),
                  ],
                ),
              ],
            ),
            body: LayoutBuilder(
              builder: (context, constraints) {
                return Row(
                  children: [
                    if (showCloud) ...[
                      SizedBox(
                        width: 250,
                        child: CloudPanel(
                          onCommand: (cmd) {
                            if (activeSessionIndex < sessions.length && sessions[activeSessionIndex].pty != null) {
                              sessions[activeSessionIndex].pty!.write(const Utf8Encoder().convert('$cmd\n'));
                            } else {
                               Process.run('sh', ['-c', cmd]);
                               ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Command sent to system.')));
                            }
                          },
                        ),
                      ),
                      const VerticalDivider(width: 1),
                    ],
                    Expanded(
                      flex: (_horizontalSplit * 1000).toInt(),
                      child: Column(
                        children: [
                          Container(
                            color: Theme.of(context).colorScheme.surfaceVariant,
                            child: Row(
                              children: [
                                Expanded(
                                  child: SingleChildScrollView(
                                    scrollDirection: Axis.horizontal,
                                    child: Row(
                                      children: sessions.asMap().entries.map((entry) {
                                        final isActive = entry.key == activeSessionIndex;
                                        return GestureDetector(
                                          onTap: () => setState(() => activeSessionIndex = entry.key),
                                          child: Container(
                                            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                                            decoration: BoxDecoration(
                                              color: isActive ? Theme.of(context).colorScheme.surface : Colors.transparent,
                                              border: Border(bottom: BorderSide(color: isActive ? Theme.of(context).colorScheme.primary : Colors.transparent, width: 2)),
                                            ),
                                            child: Text(entry.value.title, style: TextStyle(fontWeight: isActive ? FontWeight.bold : FontWeight.normal)),
                                          ),
                                        );
                                      }).toList(),
                                    ),
                                  ),
                                ),
                                IconButton(icon: const Icon(Icons.add, size: 20), onPressed: () => _addNewSession('Terminal ${sessions.length + 1}')),
                              ],
                            ),
                          ),
                          Expanded(
                            flex: (_leftVerticalSplit * 1000).toInt(),
                            child: _buildTerminal(
                              sessions[activeSessionIndex].terminal,
                              sessions[activeSessionIndex].controller,
                              focusNode: _terminalFocusNode,
                            ),
                          ),
                          if (showBottomTerminal && bottomTerminal != null) ...[
                            MouseRegion(
                              cursor: SystemMouseCursors.resizeUpDown,
                              child: GestureDetector(
                                behavior: HitTestBehavior.translucent,
                                onVerticalDragUpdate: (details) {
                                  setState(() {
                                    _leftVerticalSplit += details.delta.dy / (constraints.maxHeight - 50);
                                    _leftVerticalSplit = _leftVerticalSplit.clamp(0.1, 0.9);
                                  });
                                },
                                child: Container(height: 4, color: Theme.of(context).dividerColor),
                              ),
                            ),
                            Expanded(
                              flex: ((1 - _leftVerticalSplit) * 1000).toInt(),
                              child: _buildTerminal(bottomTerminal!, bottomTerminalController!),
                            ),
                          ],
                        ],
                      ),
                    ),
                    MouseRegion(
                      cursor: SystemMouseCursors.resizeLeftRight,
                      child: GestureDetector(
                        behavior: HitTestBehavior.translucent,
                        onHorizontalDragUpdate: (details) {
                          setState(() {
                            _horizontalSplit += details.delta.dx / constraints.maxWidth;
                            _horizontalSplit = _horizontalSplit.clamp(0.2, 0.8);
                          });
                        },
                        child: Container(width: 4, color: Theme.of(context).dividerColor),
                      ),
                    ),
                    Expanded(
                      flex: ((1 - _horizontalSplit) * 1000).toInt(),
                      child: Column(
                        children: [
                          Expanded(
                            flex: (_rightVerticalSplit * 1000).toInt(),
                            child: FileBrowser(
                              currentDir: currentDir,
                              onDirectoryChanged: (newDir) => setState(() => currentDir = newDir),
                              onFileSelected: _selectFile,
                              getFileIcon: getFileIconFromPath,
                            ),
                          ),
                          MouseRegion(
                            cursor: SystemMouseCursors.resizeUpDown,
                            child: GestureDetector(
                              behavior: HitTestBehavior.translucent,
                              onVerticalDragUpdate: (details) {
                                setState(() {
                                  _rightVerticalSplit += details.delta.dy / constraints.maxHeight;
                                  _rightVerticalSplit = _rightVerticalSplit.clamp(0.1, 0.9);
                                });
                              },
                              child: Container(height: 4, color: Theme.of(context).dividerColor),
                            ),
                          ),
                          Expanded(
                            flex: ((1 - _rightVerticalSplit) * 1000).toInt(),
                            child: Container(
                              width: double.infinity,
                              color: Theme.of(context).colorScheme.surface,
                              child: SingleChildScrollView(
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Padding(
                                      padding: const EdgeInsets.all(8.0),
                                      child: Text(previewContent, style: const TextStyle(fontFamily: 'monospace', fontSize: 10, color: Colors.grey)),
                                    ),
                                    if (rawFileContent.isNotEmpty) ...[
                                      const Divider(),
                                      HighlightView(
                                        rawFileContent,
                                        language: selectedFileExtension,
                                        theme: draculaTheme,
                                        padding: const EdgeInsets.all(8),
                                        textStyle: GoogleFonts.firaCode(fontSize: 12),
                                      ),
                                    ],
                                  ],
                                ),
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                );
              }
            ),
          ),
        ),
      ),
    );
  }
}

class CloudPanel extends StatelessWidget {
  final ValueChanged<String> onCommand;
  const CloudPanel({super.key, required this.onCommand});

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Container(padding: const EdgeInsets.all(8), color: Theme.of(context).colorScheme.secondaryContainer, child: const Row(children: [Icon(Icons.cloud_queue), SizedBox(width: 8), Text('Cloud Integration', style: TextStyle(fontWeight: FontWeight.bold))])),
        Expanded(
          child: ListView(
            children: [
              const ListTile(title: Text('Firebase', style: TextStyle(fontWeight: FontWeight.bold))),
              ListTile(title: const Text('Login'), leading: const Icon(Icons.login), dense: true, onTap: () => onCommand('firebase login')),
              ListTile(title: const Text('List Projects'), leading: const Icon(Icons.list), dense: true, onTap: () => onCommand('firebase projects:list')),
              const Divider(),
              const ListTile(title: Text('Google Cloud', style: TextStyle(fontWeight: FontWeight.bold))),
              ListTile(title: const Text('Auth Login'), leading: const Icon(Icons.vpn_key), dense: true, onTap: () => onCommand('gcloud auth login')),
              ListTile(title: const Text('List Configs'), leading: const Icon(Icons.settings), dense: true, onTap: () => onCommand('gcloud config list')),
            ],
          ),
        ),
      ],
    );
  }
}


class FileBrowser extends StatefulWidget {
  final String currentDir;
  final ValueChanged<String> onDirectoryChanged;
  final ValueChanged<File> onFileSelected;
  final IconData Function(String) getFileIcon;
  const FileBrowser({super.key, required this.currentDir, required this.onDirectoryChanged, required this.onFileSelected, required this.getFileIcon});
  @override
  State<FileBrowser> createState() => _FileBrowserState();
}

class _FileBrowserState extends State<FileBrowser> {
  List<FileSystemEntity> _entities = [];
  @override
  void initState() { super.initState(); _loadDirectory(); }
  @override
  void didUpdateWidget(FileBrowser oldWidget) { super.didUpdateWidget(oldWidget); if (oldWidget.currentDir != widget.currentDir) _loadDirectory(); }
  void _loadDirectory() {
    try {
      final dir = Directory(widget.currentDir);
      final list = dir.listSync().toList();
      list.sort((a, b) {
        if (a is Directory && b is! Directory) return -1;
        if (a is! Directory && b is Directory) return 1;
        return p.basename(a.path).toLowerCase().compareTo(p.basename(b.path).toLowerCase());
      });
      setState(() => _entities = list);
    } catch (e) { setState(() => _entities = []); }
  }
  void _showFileContextMenu(BuildContext context, Offset globalOffset, FileSystemEntity entity) {
    final RenderBox overlay = Overlay.of(context).context.findRenderObject() as RenderBox;
    final isDir = entity is Directory;
    
    showMenu(
      context: context,
      position: RelativeRect.fromRect(
        globalOffset & const Size(40, 40),
        Offset.zero & overlay.size,
      ),
      items: [
        PopupMenuItem(
          child: Row(children: [Icon(isDir ? Icons.folder_open : Icons.open_in_new, size: 18), const SizedBox(width: 8), Text(isDir ? 'Open in System' : 'Open in System')]),
          onTap: () async {
            final uri = Uri.file(entity.path);
            if (await canLaunchUrl(uri)) {
              await launchUrl(uri);
            } else {
              if (context.mounted) {
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(content: Text('Could not open ${p.basename(entity.path)}')),
                );
              }
            }
          },
        ),
      ],
    );
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Container(
          color: Theme.of(context).colorScheme.surfaceVariant,
          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
          child: Row(
            children: [
              IconButton(icon: const Icon(Icons.arrow_upward), onPressed: () => widget.onDirectoryChanged(Directory(widget.currentDir).parent.path)),
              Expanded(child: Text(widget.currentDir, overflow: TextOverflow.ellipsis, style: const TextStyle(fontWeight: FontWeight.bold))),
            ],
          ),
        ),
        Expanded(
          child: ListView.builder(
            itemCount: _entities.length,
            itemBuilder: (context, index) {
              final entity = _entities[index];
              final isDir = entity is Directory;
              return GestureDetector(
                onSecondaryTapDown: (details) => _showFileContextMenu(context, details.globalPosition, entity),
                child: ListTile(
                  leading: Icon(isDir ? Icons.folder : widget.getFileIcon(entity.path), color: isDir ? Colors.amber : null),
                  title: Text(p.basename(entity.path)),
                  dense: true,
                  onTap: () => isDir ? widget.onDirectoryChanged(entity.path) : widget.onFileSelected(File(entity.path)),
                ),
              );
            },
          ),
        ),
      ],
    );
  }
}

class FileSearchDialog extends StatefulWidget {
  final String rootDir;
  const FileSearchDialog({super.key, required this.rootDir});
  @override
  State<FileSearchDialog> createState() => _FileSearchDialogState();
}

class _FileSearchDialogState extends State<FileSearchDialog> {
  final TextEditingController _controller = TextEditingController();
  List<File> _allFiles = [];
  List<File> _filteredFiles = [];
  @override
  void initState() { super.initState(); _loadFiles(); }
  void _loadFiles() {
    try {
      final list = Directory(widget.rootDir).listSync(recursive: true, followLinks: false).whereType<File>().toList();
      setState(() { _allFiles = list; _filteredFiles = list.take(20).toList(); });
    } catch (e) {}
  }
  void _filter(String query) {
    setState(() => _filteredFiles = query.isEmpty ? _allFiles.take(20).toList() : _allFiles.where((f) => p.basename(f.path).toLowerCase().contains(query.toLowerCase())).take(50).toList());
  }
  @override
  Widget build(BuildContext context) {
    return Dialog(
      child: Container(
        width: 600, height: 400, padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            TextField(controller: _controller, autofocus: true, decoration: const InputDecoration(hintText: 'Search files (Ctrl+P)...', prefixIcon: Icon(Icons.search), border: OutlineInputBorder()), onChanged: _filter),
            const SizedBox(height: 16),
            Expanded(child: ListView.builder(itemCount: _filteredFiles.length, itemBuilder: (context, index) {
              final file = _filteredFiles[index];
              return ListTile(leading: const Icon(Icons.insert_drive_file, size: 18), title: Text(p.basename(file.path)), subtitle: Text(file.path, style: const TextStyle(fontSize: 10)), onTap: () => Navigator.of(context).pop(file));
            })),
          ],
        ),
      ),
    );
  }
}

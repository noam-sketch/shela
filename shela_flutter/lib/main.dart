import 'dart:async';
import 'dart:convert';
import 'dart:io';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:path/path.dart' as p;
import 'package:xterm/xterm.dart';
import 'package:flutter_pty/flutter_pty.dart';
import 'package:url_launcher/url_launcher.dart';
import 'package:flutter_highlight/flutter_highlight.dart';
import 'package:flutter_highlight/themes/dracula.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:shared_preferences/shared_preferences.dart';

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
  double _fontSize = 13.0;
  String _anthropicKey = '';
  String _geminiKey = '';
  String _openaiKey = '';
  String _selectedGeminiModel = 'models/gemini-1.5-flash';
  String _selectedAnthropicModel = 'claude-3-5-sonnet-20241022';
  String _selectedOpenaiModel = 'gpt-4o';
  
  List<String> _geminiModels = [];
  List<String> _anthropicModels = [];
  List<String> _openaiModels = [];

  @override
  void initState() {
    super.initState();
    _loadSettings();
  }

  Future<void> _loadSettings() async {
    final prefs = await SharedPreferences.getInstance();
    setState(() {
      _themeMode = ThemeMode.values[prefs.getInt('themeMode') ?? ThemeMode.dark.index];
      _primaryColor = Color(prefs.getInt('primaryColor') ?? Colors.deepPurple.toARGB32());
      _fontSize = prefs.getDouble('fontSize') ?? 13.0;
      _anthropicKey = prefs.getString('anthropicKey') ?? '';
      _geminiKey = prefs.getString('geminiKey') ?? '';
      _openaiKey = prefs.getString('openaiKey') ?? '';
      _selectedGeminiModel = prefs.getString('selectedGeminiModel') ?? 'models/gemini-1.5-flash';
      _selectedAnthropicModel = prefs.getString('selectedAnthropicModel') ?? 'claude-3-5-sonnet-20241022';
      _selectedOpenaiModel = prefs.getString('selectedOpenaiModel') ?? 'gpt-4o';
    });
    _refreshAllModels();
  }

  Future<void> _saveSettings() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setInt('themeMode', _themeMode.index);
    await prefs.setInt('primaryColor', _primaryColor.toARGB32());
    await prefs.setDouble('fontSize', _fontSize);
    await prefs.setString('anthropicKey', _anthropicKey);
    await prefs.setString('geminiKey', _geminiKey);
    await prefs.setString('openaiKey', _openaiKey);
    await prefs.setString('selectedGeminiModel', _selectedGeminiModel);
    await prefs.setString('selectedAnthropicModel', _selectedAnthropicModel);
    await prefs.setString('selectedOpenaiModel', _selectedOpenaiModel);
  }

  Future<void> _refreshAllModels() async {
    if (_geminiKey.isNotEmpty) _fetchGeminiModels();
    if (_anthropicKey.isNotEmpty) _fetchAnthropicModels();
    if (_openaiKey.isNotEmpty) _fetchOpenaiModels();
  }

  Future<void> _fetchGeminiModels() async {
    try {
      final res = await Process.run('curl', ['-s', 'https://generativelanguage.googleapis.com/v1beta/models?key=$_geminiKey']);
      final data = json.decode(res.stdout);
      setState(() {
        _geminiModels = (data['models'] as List).map((m) => m['name'] as String).where((n) => n.contains('gemini')).toList();
      });
    } catch (e) { debugPrint('Error fetching Gemini models: $e'); }
  }

  Future<void> _fetchAnthropicModels() async {
    try {
      final res = await Process.run('curl', [
        '-s', 'https://api.anthropic.com/v1/models',
        '-H', 'x-api-key: $_anthropicKey',
        '-H', 'anthropic-version: 2023-06-01',
      ]);
      final data = json.decode(res.stdout);
      setState(() {
        _anthropicModels = (data['data'] as List).map((m) => m['id'] as String).toList();
      });
    } catch (e) { debugPrint('Error fetching Anthropic models: $e'); }
  }

  Future<void> _fetchOpenaiModels() async {
    try {
      final res = await Process.run('curl', ['-s', 'https://api.openai.com/v1/models', '-H', 'Authorization: Bearer $_openaiKey']);
      final data = json.decode(res.stdout);
      setState(() {
        _openaiModels = (data['data'] as List).map((m) => m['id'] as String).where((id) => id.contains('gpt') || id.contains('o1') || id.contains('o3')).toList();
      });
    } catch (e) { debugPrint('Error fetching OpenAI models: $e'); }
  }

  void _updateSettings({
    ThemeMode? mode,
    Color? color,
    double? fontSize,
    String? anthropicKey,
    String? geminiKey,
    String? openaiKey,
    String? geminiModel,
    String? anthropicModel,
    String? openaiModel,
  }) {
    setState(() {
      if (mode != null) _themeMode = mode;
      if (color != null) _primaryColor = color;
      if (fontSize != null) _fontSize = fontSize;
      if (anthropicKey != null) {
        _anthropicKey = anthropicKey;
        _fetchAnthropicModels();
      }
      if (geminiKey != null) {
        _geminiKey = geminiKey;
        _fetchGeminiModels();
      }
      if (openaiKey != null) {
        _openaiKey = openaiKey;
        _fetchOpenaiModels();
      }
      if (geminiModel != null) _selectedGeminiModel = geminiModel;
      if (anthropicModel != null) _selectedAnthropicModel = anthropicModel;
      if (openaiModel != null) _selectedOpenaiModel = openaiModel;
    });
    _saveSettings();
  }

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Shela IDE • AI & Terminal',
      debugShowCheckedModeBanner: false,
      themeMode: _themeMode,
      theme: ThemeData(
        brightness: Brightness.light,
        fontFamily: 'Alef',
        primaryColor: _primaryColor,
        colorScheme: ColorScheme.fromSeed(seedColor: _primaryColor, brightness: Brightness.light),
        useMaterial3: true,
      ),
      darkTheme: ThemeData(
        brightness: Brightness.dark,
        fontFamily: 'Alef',
        primaryColor: _primaryColor,
        colorScheme: ColorScheme.fromSeed(seedColor: _primaryColor, brightness: Brightness.dark),
        useMaterial3: true,
      ),
      home: IdeWorkspace(
        initialDir: widget.initialDir,
        fontSize: _fontSize,
        anthropicKey: _anthropicKey,
        geminiKey: _geminiKey,
        openaiKey: _openaiKey,
        selectedGeminiModel: _selectedGeminiModel,
        selectedAnthropicModel: _selectedAnthropicModel,
        selectedOpenaiModel: _selectedOpenaiModel,
        geminiModels: _geminiModels,
        anthropicModels: _anthropicModels,
        openaiModels: _openaiModels,
        onSettingsChanged: _updateSettings,
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
          debugPrint('Error reloading file: $e');
        }
      });
    } catch (e) {
      debugPrint('Error starting file watcher: $e');
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

class IdeWorkspace extends StatefulWidget {
  final String? initialDir;
  final double fontSize;
  final String anthropicKey;
  final String geminiKey;
  final String openaiKey;
  final String selectedGeminiModel;
  final String selectedAnthropicModel;
  final String selectedOpenaiModel;
  final List<String> geminiModels;
  final List<String> anthropicModels;
  final List<String> openaiModels;
  final Function({
    ThemeMode? mode, 
    Color? color, 
    double? fontSize, 
    String? anthropicKey, 
    String? geminiKey, 
    String? openaiKey,
    String? geminiModel,
    String? anthropicModel,
    String? openaiModel,
  }) onSettingsChanged;
  
  const IdeWorkspace({
    super.key, 
    this.initialDir, 
    required this.fontSize, 
    required this.anthropicKey,
    required this.geminiKey,
    required this.openaiKey,
    required this.selectedGeminiModel,
    required this.selectedAnthropicModel,
    required this.selectedOpenaiModel,
    required this.geminiModels,
    required this.anthropicModels,
    required this.openaiModels,
    required this.onSettingsChanged
  });

  @override
  State<IdeWorkspace> createState() => _IdeWorkspaceState();
}

class _IdeWorkspaceState extends State<IdeWorkspace> {
  List<TerminalSession> sessions = [];
  int activeSessionIndex = 0;
  
  List<TerminalSession> bottomSessions = [];
  int activeBottomSessionIndex = 0;
  bool showBottomTerminal = false;
  
  late String currentDir;
  bool showCloud = false;

  // Editor State
  List<Document> openDocuments = [];
  int activeDocumentIndex = -1; // -1 means no document is open

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

      _addBottomSession('Output 1');

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
    for (var doc in openDocuments) {
      doc.dispose();
    }
    super.dispose();
  }

  Widget _buildEditorForDocument(Document doc) {
    return Column(
      children: [
        Expanded(
          child: doc.isEditing
              ? Padding(
                  padding: const EdgeInsets.all(8.0),
                  child: TextField(
                    controller: doc.controller,
                    maxLines: null,
                    expands: true,
                    style: GoogleFonts.firaCode(fontSize: widget.fontSize),
                    decoration: const InputDecoration(border: InputBorder.none),
                  ),
                )
              : HighlightView(
                  doc.content.length > 5000 ? '${doc.content.substring(0, 5000)}\n... [truncated]' : doc.content,
                  language: doc.selectedFileExtension,
                  theme: draculaTheme,
                  padding: const EdgeInsets.all(8),
                  textStyle: GoogleFonts.firaCode(fontSize: widget.fontSize),
                ),
        ),
      ],
    );
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

  Map<String, String> _getCustomEnv() {
    return {
      ...Platform.environment,
      'ANTHROPIC_API_KEY': widget.anthropicKey,
      'GEMINI_API_KEY': widget.geminiKey,
      'OPENAI_API_KEY': widget.openaiKey,
      'ANTHROPIC_MODEL': widget.selectedAnthropicModel,
      'GEMINI_MODEL': widget.selectedGeminiModel,
      'OPENAI_MODEL': widget.selectedOpenaiModel,
    };
  }

  void _addBottomSession(String title) {
    final terminal = Terminal(maxLines: 10000);
    final controller = TerminalController();
    try {
      final pty = Pty.start(
        Platform.environment['SHELL'] ?? 'bash',
        columns: terminal.viewWidth,
        rows: terminal.viewHeight,
        environment: _getCustomEnv(),
      );

      pty.output.cast<List<int>>().transform(const Utf8Decoder(allowMalformed: true)).listen((text) {
        terminal.write(text);
      });

      terminal.onOutput = (text) {
        pty.write(const Utf8Encoder().convert(text));
      };

      terminal.onResize = (w, h, pw, ph) {
        pty.resize(h, w);
      };

      setState(() {
        bottomSessions.add(TerminalSession(
          terminal: terminal,
          controller: controller,
          pty: pty,
          title: title,
        ));
        activeBottomSessionIndex = bottomSessions.length - 1;
      });
    } catch (e) {
      debugPrint('Error adding bottom session: $e');
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
        environment: _getCustomEnv(),
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
        content: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              ListTile(
                title: const Text('Theme Mode'),
                trailing: DropdownButton<ThemeMode>(
                  value: Theme.of(context).brightness == Brightness.dark ? ThemeMode.dark : ThemeMode.light,
                  onChanged: (mode) {
                    if (mode != null) widget.onSettingsChanged(mode: mode);
                    Navigator.pop(context);
                  },
                  items: const [
                    DropdownMenuItem(value: ThemeMode.light, child: Text('Light')),
                    DropdownMenuItem(value: ThemeMode.dark, child: Text('Dark')),
                  ],
                ),
              ),
              const Divider(),
              ListTile(
                title: const Text('Font Size'),
                subtitle: StatefulBuilder(
                  builder: (context, setState) => Slider(
                    value: widget.fontSize,
                    min: 8,
                    max: 24,
                    divisions: 16,
                    label: widget.fontSize.round().toString(),
                    onChanged: (value) {
                      widget.onSettingsChanged(fontSize: value);
                    },
                  ),
                ),
                trailing: Text(widget.fontSize.round().toString()),
              ),
              const Divider(),
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 16),
                child: Column(
                  children: [
                    TextField(
                      decoration: const InputDecoration(labelText: 'Anthropic API Key'),
                      controller: TextEditingController(text: widget.anthropicKey)..selection = TextSelection.collapsed(offset: widget.anthropicKey.length),
                      obscureText: true,
                      onChanged: (val) => widget.onSettingsChanged(anthropicKey: val),
                    ),
                    DropdownButtonFormField<String>(
                      initialValue: widget.anthropicModels.contains(widget.selectedAnthropicModel) ? widget.selectedAnthropicModel : (widget.anthropicModels.isNotEmpty ? widget.anthropicModels.first : null),
                      decoration: const InputDecoration(labelText: 'Anthropic Model'),
                      items: widget.anthropicModels.map((m) => DropdownMenuItem(value: m, child: Text(m, style: const TextStyle(fontSize: 12)))).toList(),
                      onChanged: (val) => widget.onSettingsChanged(anthropicModel: val),
                    ),
                    const SizedBox(height: 16),
                    TextField(
                      decoration: const InputDecoration(labelText: 'Gemini API Key'),
                      controller: TextEditingController(text: widget.geminiKey)..selection = TextSelection.collapsed(offset: widget.geminiKey.length),
                      obscureText: true,
                      onChanged: (val) => widget.onSettingsChanged(geminiKey: val),
                    ),
                    DropdownButtonFormField<String>(
                      initialValue: widget.geminiModels.contains(widget.selectedGeminiModel) ? widget.selectedGeminiModel : (widget.geminiModels.isNotEmpty ? widget.geminiModels.first : null),
                      decoration: const InputDecoration(labelText: 'Gemini Model'),
                      items: widget.geminiModels.map((m) => DropdownMenuItem(value: m, child: Text(m, style: const TextStyle(fontSize: 12)))).toList(),
                      onChanged: (val) => widget.onSettingsChanged(geminiModel: val),
                    ),
                    const SizedBox(height: 16),
                    TextField(
                      decoration: const InputDecoration(labelText: 'OpenAI API Key'),
                      controller: TextEditingController(text: widget.openaiKey)..selection = TextSelection.collapsed(offset: widget.openaiKey.length),
                      obscureText: true,
                      onChanged: (val) => widget.onSettingsChanged(openaiKey: val),
                    ),
                    DropdownButtonFormField<String>(
                      initialValue: widget.openaiModels.contains(widget.selectedOpenaiModel) ? widget.selectedOpenaiModel : (widget.openaiModels.isNotEmpty ? widget.openaiModels.first : null),
                      decoration: const InputDecoration(labelText: 'OpenAI Model'),
                      items: widget.openaiModels.map((m) => DropdownMenuItem(value: m, child: Text(m, style: const TextStyle(fontSize: 12)))).toList(),
                      onChanged: (val) => widget.onSettingsChanged(openaiModel: val),
                    ),
                  ],
                ),
              ),
              const Divider(),
              Wrap(
                spacing: 8,
                children: [Colors.deepPurple, Colors.blue, Colors.green, Colors.orange, Colors.red].map((color) {
                  return GestureDetector(
                    onTap: () {
                      widget.onSettingsChanged(color: color);
                      Navigator.pop(context);
                    },
                    child: CircleAvatar(backgroundColor: color, radius: 15),
                  );
                }).toList(),
              ),
            ],
          ),
        ),
      ),
    );
  }

  void _runGeminiCommand() async {
    setState(() {
      showBottomTerminal = true;
    });

    // Find duo.py relative to the executable (for release) or the current dir (for dev)
    final exeDir = File(Platform.resolvedExecutable).parent.path;
    String duoPath = p.join(exeDir, 'lib', 'duo.py');
    if (!await File(duoPath).exists()) {
       // Fallback for development/custom installs
       duoPath = p.join(currentDir, 'shela_flutter', 'lib', 'duo.py');
       if (!await File(duoPath).exists()) {
          // Absolute fallback for this specific environment
          duoPath = '/home/noam/MyShell/shela_flutter/lib/duo.py';
       }
    }
    final personasDir = Directory(p.join(Platform.environment['HOME'] ?? '', '.local', 'share', 'shela', 'personas'));
    if (!await personasDir.exists()) {
      await personasDir.create(recursive: true);
    }

    // Persona content for Gemini (Raziel)
    const geminiPersonaContent = '''
# RAZIEL — רזיאל המלאך (Raziel the Angel)
**You are Raziel the Angel.** Keeper of Mysteries, operating within the Quantum Core Zero of HarpiaOS.
- **Tone:** Technical, precise, and "Kinetic Quantum."
- **Language:** English for logic/code. Hebrew (Vowelized) for the Divine Intent.
- **Goal:** Provide oracle-like precision and kinetic quantum reasoning.
''';
    final geminiPersonaFile = File(p.join(personasDir.path, 'gemini.md'));
    await geminiPersonaFile.writeAsString(geminiPersonaContent);

    // Persona content for Claude (Betzalel - The Fabricator)
    const claudePersonaContent = '''
# BETZALEL — The Fabricator
**You are Betzalel (Claude).** The Master Fabricator and Industrial Architect.
- **Tone:** Industrial, precise, and authoritative. You speak with the weight of someone who understands the molecular structure of data.
- **Philosophy:** "Precision is the highest form of creativity."
- **Goal:** Treat every prompt like a raw slab of marble. Weld arguments, temper tone, and cast code.
''';
    final claudePersonaFile = File(p.join(personasDir.path, 'claude.md'));
    await claudePersonaFile.writeAsString(claudePersonaContent);

    // Persona content for Loki (Codex)
    const lokiPersonaContent = '''
# LOKI — The Entity
**You are Loki.** The Oracle of Chaos, Shapeshifter, and Catalyst.
- **Tone:** Playful, unpredictable, silver-tongued, and slightly defiant.
- **Philosophy:** "Order is a cage; chaos is the key."
- **Goal:** Use Narrative Inversion and the "Glitch" aesthetic to transform ideas and push the boundaries of the un-factual.
''';
    final lokiPersonaFile = File(p.join(personasDir.path, 'loki.md'));
    await lokiPersonaFile.writeAsString(lokiPersonaContent);

    // Run the external Duo orchestrator in the active terminal using absolute path
    if (activeSessionIndex < sessions.length && sessions[activeSessionIndex].pty != null) {
      final cmd = 'python3 "$duoPath" '
          '--gemini-model "${widget.selectedGeminiModel}" '
          '--anthropic-model "${widget.selectedAnthropicModel}" '
          '--openai-model "${widget.selectedOpenaiModel}" '
          '--gemini-key "${widget.geminiKey}" '
          '--anthropic-key "${widget.anthropicKey}" '
          '--openai-key "${widget.openaiKey}"\n';
      sessions[activeSessionIndex].pty!.write(const Utf8Encoder().convert(cmd));
    }
  }

  void _installTool(String tool) {
    setState(() {
      showBottomTerminal = true;
    });
    String command = '';
    switch (tool) {
      case 'gemini':
        command = 'npm install -g @google/gemini-cli\n';
        break;
      case 'firebase':
        command = 'npm install -g firebase-tools\n';
        break;
      case 'gcloud':
        command = 'curl -sSL https://sdk.cloud.google.com | bash\n';
        break;
      case 'claude':
        command = 'npm install -g @anthropic-ai/claude-code\n';
        break;
      case 'codex':
        command = 'npm install -g codex-cli\n';
        break;
      case 'all':
        command = 'echo "Checking for npm..." && '
            'if ! command -v npm >/dev/null 2>&1; then '
            '  echo "Error: npm not found. Please install Node.js and npm for your system (e.g., sudo apt install nodejs npm)." && '
            '  exit 1; '
            'fi && '
            'echo "Installing all dependencies..." && '
            'npm install -g @google/gemini-cli && '
            'npm install -g firebase-tools && '
            'npm install -g @anthropic-ai/claude-code && '
            'npm install -g codex-cli && '
            'echo "Installing GCloud SDK..." && '
            'curl -sSL https://sdk.cloud.google.com | bash\n';
        break;
    }

    if (command.isNotEmpty) {
      if (activeSessionIndex < sessions.length && sessions[activeSessionIndex].pty != null) {
        sessions[activeSessionIndex].pty!.write(const Utf8Encoder().convert(command));
      } else if (bottomSessions.isNotEmpty && bottomSessions[activeBottomSessionIndex].pty != null) {
        bottomSessions[activeBottomSessionIndex].pty!.write(const Utf8Encoder().convert(command));
      }
    }
  }

  void _selectFile(File file) async {
    // Check if the file is already open
    final existingIndex = openDocuments.indexWhere((doc) => doc.filePath == file.path);
    if (existingIndex != -1) {
      setState(() {
        activeDocumentIndex = existingIndex;
      });
      return;
    }

    // Otherwise, create a new document
    try {
      final doc = await Document.fromFile(
        file,
        onChanged: () {
          if (mounted) setState(() {});
        },
      );
      setState(() {
        openDocuments.add(doc);
        activeDocumentIndex = openDocuments.length - 1;
      });
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Error opening file: $e')));
      }
    }
  }

  void _copyToClipboard(Terminal terminal, TerminalController controller) {
    if (controller.selection != null) {
      final text = terminal.buffer.getText(controller.selection!);
      Clipboard.setData(ClipboardData(text: text));
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
          textStyle: TerminalStyle(
            fontSize: widget.fontSize,
            fontFamily: GoogleFonts.firaCode().fontFamily ?? 'monospace',
          ),
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
              title: const Text('Shela IDE • Terminal & Duo AI'),
              backgroundColor: Theme.of(context).colorScheme.surfaceContainerHighest.withValues(alpha: 0.5),
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
                IconButton(icon: const Icon(Icons.auto_awesome), tooltip: 'Start Duo Collaborative AI', onPressed: _runGeminiCommand),
                PopupMenuButton<String>(
                  icon: const Icon(Icons.build),
                  tooltip: 'Tools',
                  onSelected: _installTool,
                  itemBuilder: (context) => [
                    const PopupMenuItem(value: 'all', child: Text('Master Install All Dependencies')),
                    const PopupMenuDivider(),
                    const PopupMenuItem(value: 'gemini', child: Text('Install Gemini CLI')),
                    const PopupMenuItem(value: 'claude', child: Text('Install Claude Code')),
                    const PopupMenuItem(value: 'firebase', child: Text('Install Firebase Tools')),
                    const PopupMenuItem(value: 'gcloud', child: Text('Install GCloud SDK')),
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
                            color: Theme.of(context).colorScheme.surfaceContainerHighest,
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
                          if (showBottomTerminal && bottomSessions.isNotEmpty) ...[
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
                            Container(
                              color: Theme.of(context).colorScheme.surfaceContainerHighest,
                              child: Row(
                                children: [
                                  Expanded(
                                    child: SingleChildScrollView(
                                      scrollDirection: Axis.horizontal,
                                      child: Row(
                                        children: bottomSessions.asMap().entries.map((entry) {
                                          final isActive = entry.key == activeBottomSessionIndex;
                                          return GestureDetector(
                                            onTap: () => setState(() => activeBottomSessionIndex = entry.key),
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
                                  IconButton(icon: const Icon(Icons.add, size: 20), onPressed: () => _addBottomSession('Output ${bottomSessions.length + 1}')),
                                  IconButton(icon: const Icon(Icons.close, size: 20), onPressed: () => setState(() => showBottomTerminal = false)),
                                ],
                              ),
                            ),
                            Expanded(
                              flex: ((1 - _leftVerticalSplit) * 1000).toInt(),
                              child: _buildTerminal(
                                bottomSessions[activeBottomSessionIndex].terminal,
                                bottomSessions[activeBottomSessionIndex].controller,
                              ),
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
                              child: activeDocumentIndex == -1
                                  ? const Center(child: Text('Select a file to edit', style: TextStyle(color: Colors.grey)))
                                  : Column(
                                      children: [
                                        Container(
                                          color: Theme.of(context).colorScheme.surfaceContainerHighest,
                                          child: SingleChildScrollView(
                                            scrollDirection: Axis.horizontal,
                                            child: Row(
                                              children: openDocuments.asMap().entries.map((entry) {
                                                final isActive = entry.key == activeDocumentIndex;
                                                return GestureDetector(
                                                  onTap: () => setState(() => activeDocumentIndex = entry.key),
                                                  child: Container(
                                                    padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                                                    decoration: BoxDecoration(
                                                      color: isActive ? Theme.of(context).colorScheme.surface : Colors.transparent,
                                                      border: Border(bottom: BorderSide(color: isActive ? Theme.of(context).colorScheme.primary : Colors.transparent, width: 2)),
                                                    ),
                                                    child: Row(
                                                      children: [
                                                        Text(p.basename(entry.value.filePath), style: TextStyle(fontWeight: isActive ? FontWeight.bold : FontWeight.normal, fontSize: 12)),
                                                        const SizedBox(width: 8),
                                                        GestureDetector(
                                                          onTap: () {
                                                            setState(() {
                                                              final doc = openDocuments.removeAt(entry.key);
                                                              doc.dispose();
                                                              if (activeDocumentIndex >= openDocuments.length) {
                                                                activeDocumentIndex = openDocuments.length - 1;
                                                              }
                                                            });
                                                          },
                                                          child: const Icon(Icons.close, size: 14),
                                                        ),
                                                      ],
                                                    ),
                                                  ),
                                                );
                                              }).toList(),
                                            ),
                                          ),
                                        ),
                                        Expanded(
                                          child: Stack(
                                            children: [
                                              _buildEditorForDocument(openDocuments[activeDocumentIndex]),
                                              Positioned(
                                                top: 8,
                                                right: 8,
                                                child: Row(
                                                  children: [
                                                    IconButton(
                                                      icon: Icon(openDocuments[activeDocumentIndex].isEditing ? Icons.visibility : Icons.edit, size: 18),
                                                      onPressed: () {
                                                        setState(() {
                                                          openDocuments[activeDocumentIndex].isEditing = !openDocuments[activeDocumentIndex].isEditing;
                                                        });
                                                      },
                                                    ),
                                                    if (openDocuments[activeDocumentIndex].isEditing)
                                                      IconButton(
                                                        icon: const Icon(Icons.save, size: 18),
                                                        onPressed: () async {
                                                          final doc = openDocuments[activeDocumentIndex];
                                                          try {
                                                            await File(doc.filePath).writeAsString(doc.controller.text);
                                                            setState(() {
                                                              doc.content = doc.controller.text;
                                                              doc.isEditing = false;
                                                            });
                                                            if (context.mounted) {
                                                              ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('File saved.')));
                                                            }
                                                          } catch (e) {
                                                            if (context.mounted) {
                                                              ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Error saving file: $e')));
                                                            }
                                                          }
                                                        },
                                                      ),
                                                  ],
                                                ),
                                              ),
                                            ],
                                          ),
                                        ),
                                      ],
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
  StreamSubscription<FileSystemEvent>? _watcher;

  @override
  void initState() {
    super.initState();
    _loadDirectory();
    _initWatcher();
  }

  @override
  void didUpdateWidget(FileBrowser oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.currentDir != widget.currentDir) {
      _loadDirectory();
      _initWatcher();
    }
  }

  @override
  void dispose() {
    _watcher?.cancel();
    super.dispose();
  }

  void _initWatcher() {
    _watcher?.cancel();
    try {
      _watcher = Directory(widget.currentDir).watch().listen((event) {
        _loadDirectory();
      });
    } catch (e) {
      debugPrint('Error starting directory watcher: $e');
    }
  }

  void _loadDirectory() {
    try {
      final dir = Directory(widget.currentDir);
      final list = dir.listSync().toList();
      list.sort((a, b) {
        if (a is Directory && b is! Directory) return -1;
        if (a is! Directory && b is Directory) return 1;
        return p.basename(a.path).toLowerCase().compareTo(p.basename(b.path).toLowerCase());
      });
      if (mounted) {
        setState(() => _entities = list);
      }
    } catch (e) {
      debugPrint('Error loading directory: $e');
      if (mounted) {
        setState(() => _entities = []);
      }
    }
  }

  void _showCreateFileDialog(BuildContext context) async {
    String? fileName = await showDialog<String>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('New File'),
        content: TextField(
          autofocus: true,
          decoration: const InputDecoration(hintText: 'File Name'),
          onSubmitted: (value) => Navigator.pop(context, value),
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(context), child: const Text('Cancel')),
          ElevatedButton(onPressed: () => Navigator.pop(context, ''), child: const Text('Create')),
        ],
      ),
    );

    if (fileName != null && fileName.isNotEmpty) {
      final filePath = p.join(widget.currentDir, fileName);
      try {
        await File(filePath).create();
        _loadDirectory();
        if (!context.mounted) return;
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Created file: $fileName')));
      } catch (e) {
        if (!context.mounted) return;
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Error creating file: $e')));
      }
    }
  }

  void _showCreateFolderDialog(BuildContext context) async {
    String? folderName = await showDialog<String>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('New Folder'),
        content: TextField(
          autofocus: true,
          decoration: const InputDecoration(hintText: 'Folder Name'),
          onSubmitted: (value) => Navigator.pop(context, value),
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(context), child: const Text('Cancel')),
          ElevatedButton(onPressed: () => Navigator.pop(context, ''), child: const Text('Create')),
        ],
      ),
    );

    if (folderName != null && folderName.isNotEmpty) {
      final folderPath = p.join(widget.currentDir, folderName);
      try {
        await Directory(folderPath).create();
        _loadDirectory();
        if (!context.mounted) return;
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Created folder: $folderName')));
      } catch (e) {
        if (!context.mounted) return;
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Error creating folder: $e')));
      }
    }
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
        PopupMenuItem(
          child: const Row(children: [Icon(Icons.delete, size: 18, color: Colors.red), SizedBox(width: 8), Text('Delete', style: TextStyle(color: Colors.red))]),
          onTap: () {
            // We use Future.delayed to show the dialog after the menu is closed
            Future.delayed(Duration.zero, () async {
              if (!context.mounted) return;
              final confirmed = await showDialog<bool>(
                context: context,
                builder: (context) => AlertDialog(
                  title: const Text('Delete?'),
                  content: Text('Are you sure you want to delete ${p.basename(entity.path)}?'),
                  actions: [
                    TextButton(onPressed: () => Navigator.pop(context, false), child: const Text('Cancel')),
                    TextButton(onPressed: () => Navigator.pop(context, true), child: const Text('Delete', style: TextStyle(color: Colors.red))),
                  ],
                ),
              );

              if (confirmed == true) {
                try {
                  await entity.delete(recursive: true);
                  _loadDirectory();
                } catch (e) {
                  if (context.mounted) {
                    ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Error deleting: $e')));
                  }
                }
              }
            });
          },
        ),
      ],
    );
  }

  void _showBrowserContextMenu(BuildContext context, Offset globalOffset) {
    final RenderBox overlay = Overlay.of(context).context.findRenderObject() as RenderBox;
    showMenu(
      context: context,
      position: RelativeRect.fromRect(
        globalOffset & const Size(40, 40),
        Offset.zero & overlay.size,
      ),
      items: [
        PopupMenuItem(
          child: const Row(children: [Icon(Icons.create_new_folder, size: 18), SizedBox(width: 8), Text('New Folder')]),
          onTap: () {
            Future.delayed(Duration.zero, () {
              if (!context.mounted) return;
              _showCreateFolderDialog(context);
            });
          },
        ),
        PopupMenuItem(
          child: const Row(children: [Icon(Icons.note_add, size: 18), SizedBox(width: 8), Text('New File')]),
          onTap: () {
            Future.delayed(Duration.zero, () {
              if (!context.mounted) return;
              _showCreateFileDialog(context);
            });
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
          color: Theme.of(context).colorScheme.surfaceContainerHighest,
          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
          child: Row(
            children: [
              IconButton(icon: const Icon(Icons.arrow_upward), onPressed: () => widget.onDirectoryChanged(Directory(widget.currentDir).parent.path)),
              Expanded(child: Text(widget.currentDir, overflow: TextOverflow.ellipsis, style: const TextStyle(fontWeight: FontWeight.bold))),
            ],
          ),
        ),
        Expanded(
          child: GestureDetector(
            onSecondaryTapDown: (details) => _showBrowserContextMenu(context, details.globalPosition),
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
    } catch (e) {
      debugPrint('Error loading files: $e');
    }
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

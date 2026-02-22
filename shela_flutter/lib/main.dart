import 'dart:async';
import 'dart:convert';
import 'dart:io';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter/gestures.dart';
import 'package:flutter_pty/flutter_pty.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:shela_flutter/models.dart';
import 'package:shela_flutter/models/telemetry_data.dart';
import 'package:shela_flutter/theme.dart';
import 'package:shela_flutter/widgets/file_search_dialog.dart';
import 'package:shela_flutter/widgets/telemetry_status_bar.dart';
import 'package:xterm/xterm.dart';
import 'package:path/path.dart' as p;
import 'package:flutter_highlight/flutter_highlight.dart';
import 'package:flutter_highlight/themes/dracula.dart';
import 'package:url_launcher/url_launcher.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:window_manager/window_manager.dart';

void main(List<String> args) async {
  WidgetsFlutterBinding.ensureInitialized();
  await windowManager.ensureInitialized();
  WindowOptions windowOptions = const WindowOptions(size: Size(1280, 800), center: true, backgroundColor: Colors.transparent, skipTaskbar: false, titleBarStyle: TitleBarStyle.hidden);
  windowManager.waitUntilReadyToShow(windowOptions, () async { await windowManager.show(); await windowManager.focus(); });
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
  String _currentThemeName = 'Catppuccin Mocha';
  double _globalFontSize = 13.0;
  String _geminiKey = '';
  String _selectedGeminiModel = 'models/gemini-1.5-flash';
  List<String> _geminiModels = [];

  @override
  void initState() { super.initState(); _loadSettings(); }
  Future<void> _loadSettings() async {
    final prefs = await SharedPreferences.getInstance();
    setState(() { _currentThemeName = prefs.getString('themeName') ?? 'Catppuccin Mocha'; _globalFontSize = prefs.getDouble('globalFontSize') ?? 13.0; _geminiKey = prefs.getString('geminiKey') ?? ''; _selectedGeminiModel = prefs.getString('selectedGeminiModel') ?? 'models/gemini-1.5-flash'; });
    if (_geminiKey.isNotEmpty) _fetchGeminiModels();
  }
  Future<void> _saveSettings() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('themeName', _currentThemeName); await prefs.setDouble('globalFontSize', _globalFontSize); await prefs.setString('geminiKey', _geminiKey); await prefs.setString('selectedGeminiModel', _selectedGeminiModel);
  }
  Future<void> _fetchGeminiModels() async {
    try {
      final client = HttpClient(); final request = await client.getUrl(Uri.parse('https://generativelanguage.googleapis.com/v1beta/models?key=$_geminiKey'));
      final response = await request.close();
      if (response.statusCode == 200) {
        final jsonStr = await response.transform(utf8.decoder).join(); final data = json.decode(jsonStr);
        if (mounted) setState(() { _geminiModels = (data['models'] as List).map((m) => m['name'] as String).where((n) => n.contains('gemini')).toList(); });
      }
      client.close();
    } catch (e) { debugPrint('Error: $e'); }
  }
  void _updateSettings({String? themeName, double? fontSize, String? geminiKey, String? geminiModel}) {
    setState(() { if (themeName != null) _currentThemeName = themeName; if (fontSize != null) _globalFontSize = fontSize; if (geminiKey != null) { _geminiKey = geminiKey; _fetchGeminiModels(); } if (geminiModel != null) _selectedGeminiModel = geminiModel; });
    _saveSettings();
  }
  @override
  Widget build(BuildContext context) {
    final theme = shelaThemes[_currentThemeName] ?? catppuccinMochaTheme;
    return MaterialApp(
      title: 'Shela IDE', debugCheckedModeBanner: false,
      theme: theme.copyWith(textTheme: GoogleFonts.notoSansHebrewTextTheme(theme.textTheme)),
      home: IdeWorkspace(initialDir: widget.initialDir, geminiKey: _geminiKey, selectedGeminiModel: _selectedGeminiModel, geminiModels: _geminiModels, fontSize: _globalFontSize, currentThemeName: _currentThemeName, onSettingsChanged: _updateSettings),
    );
  }
}

class IdeWorkspace extends StatefulWidget {
  final String? initialDir;
  final String geminiKey;
  final String selectedGeminiModel;
  final List<String> geminiModels;
  final double fontSize;
  final String currentThemeName;
  final Function({String? themeName, double? fontSize, String? geminiKey, String? geminiModel}) onSettingsChanged;
  const IdeWorkspace({super.key, this.initialDir, required this.geminiKey, required this.selectedGeminiModel, required this.geminiModels, required this.fontSize, required this.currentThemeName, required this.onSettingsChanged});
  @override
  State<IdeWorkspace> createState() => _IdeWorkspaceState();
}

class _IdeWorkspaceState extends State<IdeWorkspace> with TickerProviderStateMixin {
  late TabController _topTabController;
  late TabController _bottomTabController;
  List<TerminalSession> topSessions = [];
  List<TerminalSession> bottomSessions = [];
  List<Document> openDocuments = [];
  int activeDocumentIndex = -1;
  late String currentDir;
  bool showCloud = false;
  double _horizontalSplit = 0.6;
  double _leftVerticalSplit = 0.7;
  double _rightVerticalSplit = 0.5;
  TelemetryData? _telemetryData;
  Timer? _telemetryTimer;
  final TextEditingController _promptController = TextEditingController();
  final List<String> _promptBuffer = [];
  String _activeTerminalCwd = '';

  @override
  void initState() {
    super.initState();
    currentDir = widget.initialDir ?? Platform.environment['HOME'] ?? '/';
    _activeTerminalCwd = currentDir;
    _topTabController = TabController(length: 0, vsync: this);
    _bottomTabController = TabController(length: 0, vsync: this);
    _loadLayoutSettings();
    WidgetsBinding.instance.addPostFrameCallback((_) { _addNewTopSession('Terminal 1'); _addNewBottomSession('Output 1'); });
    _startTelemetryTimer();
  }

  Future<void> _loadLayoutSettings() async {
    final prefs = await SharedPreferences.getInstance();
    setState(() { _horizontalSplit = prefs.getDouble('horizontalSplit') ?? 0.6; _leftVerticalSplit = prefs.getDouble('leftVerticalSplit') ?? 0.7; _rightVerticalSplit = prefs.getDouble('rightVerticalSplit') ?? 0.5; });
  }
  Future<void> _saveLayoutSettings() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setDouble('horizontalSplit', _horizontalSplit); await prefs.setDouble('leftVerticalSplit', _leftVerticalSplit); await prefs.setDouble('rightVerticalSplit', _rightVerticalSplit);
  }
  void _startTelemetryTimer() {
    _telemetryTimer = Timer.periodic(const Duration(milliseconds: 500), (timer) async {
      try {
        final file = File(p.join(currentDir, 'usage.json'));
        if (await file.exists()) {
          final List<dynamic> entries = jsonDecode(await file.readAsString());
          if (entries.isNotEmpty && mounted) setState(() => _telemetryData = TelemetryData.fromJson(entries.last));
        }
      } catch (_) {}
    });
  }
  @override
  void dispose() { _telemetryTimer?.cancel(); _promptController.dispose(); _topTabController.dispose(); _bottomTabController.dispose(); super.dispose(); }

  void _addNewTopSession(String title) {
    final session = _createSession(title);
    setState(() { topSessions.add(session); _topTabController = TabController(length: topSessions.length, vsync: this, initialIndex: topSessions.length - 1); _topTabController.addListener(() { if (mounted) setState(() {}); }); });
  }
  void _addNewBottomSession(String title) {
    final session = _createSession(title);
    setState(() { bottomSessions.add(session); _bottomTabController = TabController(length: bottomSessions.length, vsync: this, initialIndex: bottomSessions.length - 1); _bottomTabController.addListener(() { if (mounted) setState(() {}); }); });
  }
  TerminalSession _createSession(String title) {
    final terminal = Terminal(maxLines: 10000);
    final controller = TerminalController();
    if (Platform.environment.containsKey('FLUTTER_TEST')) return TerminalSession(terminal: terminal, controller: controller, pty: null, title: title);
    final pty = Pty.start(Platform.environment['SHELL'] ?? 'bash', columns: terminal.viewWidth, rows: terminal.viewHeight, workingDirectory: currentDir);
    pty.output.cast<List<int>>().transform(const Utf8Decoder(allowMalformed: true)).listen(terminal.write);
    terminal.onOutput = (text) => pty.write(utf8.encode(text));
    terminal.onTitleChange = (t) { if (t.startsWith('SHELA_CWD:') && mounted) { final val = t.substring(10); if (_topTabController.index < topSessions.length && topSessions[_topTabController.index].terminal == terminal) setState(() { _activeTerminalCwd = val; }); } };
    terminal.onResize = (w, h, pw, ph) => pty.resize(h, w);
    pty.write(utf8.encode('PROMPT_COMMAND=\'printf "\\e]2;SHELA_CWD:%s\\x07" "\$(pwd)"\'\nclear\n'));
    return TerminalSession(terminal: terminal, controller: controller, pty: pty, title: title);
  }

  void _selectFile(File file) async {
    final idx = openDocuments.indexWhere((doc) => doc.filePath == file.path);
    if (idx != -1) { setState(() => activeDocumentIndex = idx); return; }
    try {
      final doc = await Document.fromFile(file, onChanged: () { if (mounted) setState(() {}); });
      setState(() { openDocuments.add(doc); activeDocumentIndex = openDocuments.length - 1; });
    } catch (e) { if (mounted) ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Error: $e'))); }
  }

  void _showSettings() {
    showDialog(context: context, builder: (context) => AlertDialog(
      title: const Text('Settings'),
      content: SingleChildScrollView(child: Column(mainAxisSize: MainAxisSize.min, children: [
        DropdownButtonFormField<String>(initialValue: widget.currentThemeName, decoration: const InputDecoration(labelText: 'Theme'), items: shelaThemes.keys.map((t) => DropdownMenuItem(value: t, child: Text(t))).toList(), onChanged: (val) => widget.onSettingsChanged(themeName: val)),
        const SizedBox(height: 16), const Text('Font Size'),
        Slider(value: widget.fontSize, min: 8, max: 24, divisions: 16, label: widget.fontSize.round().toString(), onChanged: (val) => widget.onSettingsChanged(fontSize: val)),
        const Divider(), TextField(decoration: const InputDecoration(labelText: 'Gemini API Key'), controller: TextEditingController(text: widget.geminiKey), obscureText: true, onChanged: (val) => widget.onSettingsChanged(geminiKey: val)),
        DropdownButtonFormField<String>(initialValue: widget.geminiModels.contains(widget.selectedGeminiModel) ? widget.selectedGeminiModel : null, decoration: const InputDecoration(labelText: 'Gemini Model'), items: widget.geminiModels.map((m) => DropdownMenuItem(value: m, child: Text(m))).toList(), onChanged: (val) => widget.onSettingsChanged(geminiModel: val)),
      ])),
      actions: [TextButton(onPressed: () => Navigator.pop(context), child: const Text('Close'))],
    ));
  }

  void _runDuo() {
    if (topSessions.isEmpty) return;
    final session = topSessions[_topTabController.index];
    if (session.pty != null) {
      final duoPath = p.join(p.dirname(Platform.resolvedExecutable), 'lib', 'duo.py');
      session.pty!.write(utf8.encode(' clear; python3 "$duoPath" --gemini-key "${widget.geminiKey}" --gemini-model "${widget.selectedGeminiModel}"\n'));
    }
  }

  void _sendBuffer() {
    if (_promptBuffer.isEmpty) return;
    final session = topSessions[_topTabController.index];
    if (session.pty != null) { session.pty!.write(utf8.encode('${_promptBuffer.join('\n')}\n')); setState(() => _promptBuffer.clear()); }
  }

  void _showTerminalContextMenu(BuildContext context, Offset globalOffset, Terminal terminal, TerminalController controller) {
    final RenderBox overlay = Navigator.of(context).overlay!.context.findRenderObject() as RenderBox;
    showMenu(context: context, position: RelativeRect.fromRect(globalOffset & const Size(40, 40), Offset.zero & overlay.size), items: [
      PopupMenuItem(child: const Text('Copy'), onTap: () { if (controller.selection != null) Clipboard.setData(ClipboardData(text: terminal.buffer.getText(controller.selection!))); }),
      PopupMenuItem(child: const Text('Paste'), onTap: () async { final data = await Clipboard.getData(Clipboard.kTextPlain); if (data?.text != null) terminal.paste(data!.text!); }),
    ]);
  }

  Widget _buildTerminalView(TerminalSession session) {
    return Listener(
      onPointerDown: (e) { if (e.buttons == kSecondaryButton) _showTerminalContextMenu(context, e.position, session.terminal, session.controller); },
      child: TerminalView(session.terminal, controller: session.controller, autofocus: true, backgroundOpacity: 0.7, textStyle: TerminalStyle(fontSize: widget.fontSize, fontFamily: GoogleFonts.notoSansHebrew().fontFamily ?? 'monospace')),
    );
  }

  Widget _buildTitleBar() {
    return Container(height: 40, color: Theme.of(context).colorScheme.surfaceContainerHighest, child: Row(children: [
      const DragToMoveArea(child: Padding(padding: EdgeInsets.symmetric(horizontal: 16), child: Center(child: Text('Shela IDE', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 12))))),
      PopupMenuButton<String>(icon: const Icon(Icons.menu, size: 18), onSelected: (v) { if (v == 'settings') _showSettings(); }, itemBuilder: (c) => [const PopupMenuItem(value: 'settings', child: Text('Settings'))]),
      IconButton(icon: const Icon(Icons.cloud, size: 18), onPressed: () => setState(() => showCloud = !showCloud)),
      IconButton(icon: const Icon(Icons.search, size: 18), onPressed: () => showDialog(context: context, builder: (c) => FileSearchDialog(onFileSelected: (p) { Navigator.pop(context); _selectFile(File(p)); }))),
      IconButton(icon: const Icon(Icons.auto_awesome, size: 18), onPressed: _runDuo),
      const Expanded(child: DragToMoveArea(child: SizedBox.expand())),
      IconButton(icon: const Icon(Icons.remove, size: 18), onPressed: () => windowManager.minimize()),
      IconButton(icon: const Icon(Icons.crop_square, size: 18), onPressed: () async { if (await windowManager.isMaximized()) windowManager.unmaximize(); else windowManager.maximize(); }),
      IconButton(icon: const Icon(Icons.close, size: 18, color: Colors.red), onPressed: () => windowManager.close()),
    ]));
  }

  @override
  Widget build(BuildContext context) {
    if (topSessions.isEmpty) return const Scaffold(body: Center(child: CircularProgressIndicator()));
    return Scaffold(body: Column(children: [
      _buildTitleBar(),
      Expanded(child: LayoutBuilder(builder: (context, constraints) {
        return Row(children: [
          if (showCloud) ...[SizedBox(width: 200, child: CloudPanel(onCommand: (cmd) { if (topSessions[_topTabController.index].pty != null) topSessions[_topTabController.index].pty!.write(utf8.encode('$cmd\n')); })), const VerticalDivider(width: 1)],
          Expanded(flex: (_horizontalSplit * 1000).toInt(), child: Column(children: [
            Expanded(flex: (_leftVerticalSplit * 1000).toInt(), child: Column(children: [
              Row(children: [Expanded(child: TabBar(controller: _topTabController, isScrollable: true, tabs: topSessions.map((s) => Tab(text: s.title)).toList())), IconButton(icon: const Icon(Icons.add, size: 20), onPressed: () => _addNewTopSession('Terminal ${topSessions.length + 1}'))]),
              Expanded(child: TabBarView(controller: _topTabController, children: topSessions.map((s) => _buildTerminalView(s)).toList())),
              Container(decoration: BoxDecoration(color: Theme.of(context).colorScheme.surface, border: Border(top: BorderSide(color: Theme.of(context).dividerColor))), padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4), child: Column(mainAxisSize: MainAxisSize.min, children: [
                if (_promptBuffer.isNotEmpty) Padding(padding: const EdgeInsets.only(bottom: 4), child: SingleChildScrollView(scrollDirection: Axis.horizontal, child: Row(children: _promptBuffer.map((p) => Padding(padding: const EdgeInsets.only(right: 4), child: Chip(label: Text(p, style: const TextStyle(fontSize: 10)), padding: EdgeInsets.zero, visualDensity: VisualDensity.compact))).toList()))),
                Text('CWD: $_activeTerminalCwd', style: const TextStyle(fontSize: 10, color: Colors.grey), overflow: TextOverflow.ellipsis),
                CallbackShortcuts(bindings: { const SingleActivator(LogicalKeyboardKey.enter, control: true): _sendBuffer }, child: TextField(controller: _promptController, style: TextStyle(fontSize: widget.fontSize), decoration: const InputDecoration(hintText: 'Ctrl+Enter to send...', isDense: true, border: InputBorder.none), onSubmitted: (v) { if (v.isNotEmpty) { setState(() => _promptBuffer.add(v)); _promptController.clear(); } })),
              ])),
            ])),
            GestureDetector(onVerticalDragUpdate: (d) { setState(() { _leftVerticalSplit += d.delta.dy / constraints.maxHeight; _leftVerticalSplit = _leftVerticalSplit.clamp(0.1, 0.9); }); _saveLayoutSettings(); }, child: MouseRegion(cursor: SystemMouseCursors.resizeUpDown, child: Container(height: 4, color: Theme.of(context).dividerColor))),
            Expanded(flex: ((1 - _leftVerticalSplit) * 1000).toInt(), child: Column(children: [
              Row(children: [Expanded(child: TabBar(controller: _bottomTabController, isScrollable: true, tabs: bottomSessions.map((s) => Tab(text: s.title)).toList())), IconButton(icon: const Icon(Icons.add, size: 20), onPressed: () => _addNewBottomSession('Output ${bottomSessions.length + 1}'))]),
              Expanded(child: TabBarView(controller: _bottomTabController, children: bottomSessions.map((s) => _buildTerminalView(s)).toList())),
              TelemetryStatusBar(data: _telemetryData),
            ])),
          ])),
          GestureDetector(onHorizontalDragUpdate: (d) { setState(() { _horizontalSplit += d.delta.dx / constraints.maxWidth; _horizontalSplit = _horizontalSplit.clamp(0.2, 0.8); }); _saveLayoutSettings(); }, child: MouseRegion(cursor: SystemMouseCursors.resizeLeftRight, child: Container(width: 4, color: Theme.of(context).dividerColor))),
          Expanded(flex: ((1 - _horizontalSplit) * 1000).toInt(), child: Column(children: [
            Expanded(flex: (_rightVerticalSplit * 1000).toInt(), child: FileBrowser(currentDir: currentDir, terminalCwd: _activeTerminalCwd, onDirectoryChanged: (d) => setState(() => currentDir = d), onFileSelected: _selectFile, getFileIcon: getFileIconFromPath, fontSize: widget.fontSize)),
            GestureDetector(onVerticalDragUpdate: (d) { setState(() { _rightVerticalSplit += d.delta.dy / constraints.maxHeight; _rightVerticalSplit = _rightVerticalSplit.clamp(0.1, 0.9); }); _saveLayoutSettings(); }, child: MouseRegion(cursor: SystemMouseCursors.resizeUpDown, child: Container(height: 4, color: Theme.of(context).dividerColor))),
            Expanded(flex: ((1 - _rightVerticalSplit) * 1000).toInt(), child: activeDocumentIndex == -1 ? const Center(child: Text('No file')) : EditorView(document: openDocuments[activeDocumentIndex], fontSize: widget.fontSize)),
          ])),
        ]);
      })),
    ]));
  }
}

class EditorView extends StatelessWidget {
  final Document document; final double fontSize;
  const EditorView({super.key, required this.document, required this.fontSize});
  @override
  Widget build(BuildContext context) {
    return Column(children: [
      Container(padding: const EdgeInsets.all(4), color: Theme.of(context).colorScheme.surfaceContainerHighest, child: Row(children: [Text(p.basename(document.filePath), style: const TextStyle(fontSize: 11)), const Spacer(), IconButton(icon: const Icon(Icons.save, size: 14), onPressed: () => File(document.filePath).writeAsString(document.controller.text))])),
      Expanded(child: document.isEditing ? TextField(controller: document.controller, maxLines: null, expands: true, style: TextStyle(fontSize: fontSize)) : HighlightView(document.content, language: document.selectedFileExtension, theme: draculaTheme, padding: const EdgeInsets.all(8), textStyle: TextStyle(fontSize: fontSize))),
    ]);
  }
}

class CloudPanel extends StatelessWidget {
  final ValueChanged<String> onCommand;
  const CloudPanel({super.key, required this.onCommand});
  @override
  Widget build(BuildContext context) {
    return ListView(children: [
      const ListTile(title: Text('Git / GitHub', style: TextStyle(fontWeight: FontWeight.bold))),
      ListTile(title: const Text('Status'), dense: true, onTap: () => onCommand('git status')),
      ListTile(title: const Text('Push'), dense: true, onTap: () => onCommand('git push')),
      ListTile(title: const Text('GH Auth Login'), dense: true, onTap: () => onCommand('gh auth login')),
      const Divider(),
      const ListTile(title: Text('Firebase', style: TextStyle(fontWeight: FontWeight.bold))),
      ListTile(title: const Text('FB Login'), dense: true, onTap: () => onCommand('firebase login')),
      const Divider(),
      const ListTile(title: Text('Gemini', style: TextStyle(fontWeight: FontWeight.bold))),
      ListTile(title: const Text('Gemini Login'), dense: true, onTap: () => onCommand('gemini auth login')),
    ]);
  }
}

class FileBrowser extends StatefulWidget {
  final String currentDir; final String terminalCwd; final ValueChanged<String> onDirectoryChanged; final ValueChanged<File> onFileSelected; final IconData Function(String) getFileIcon; final double fontSize;
  const FileBrowser({super.key, required this.currentDir, required this.terminalCwd, required this.onDirectoryChanged, required this.onFileSelected, required this.getFileIcon, required this.fontSize});
  @override
  State<FileBrowser> createState() => _FileBrowserState();
}

class _FileBrowserState extends State<FileBrowser> {
  List<FileSystemEntity> _entities = [];
  @override
  void initState() { super.initState(); _load(); }
  @override
  void didUpdateWidget(FileBrowser old) { super.didUpdateWidget(old); if (old.currentDir != widget.currentDir) _load(); }
  void _load() { try { final list = Directory(widget.currentDir).listSync().toList(); list.sort((a, b) { if (a is Directory && b is! Directory) return -1; if (a is! Directory && b is Directory) return 1; return p.basename(a.path).compareTo(p.basename(b.path)); }); setState(() => _entities = list); } catch (_) { setState(() => _entities = []); } }
  void _showItemMenu(BuildContext context, Offset globalOffset, FileSystemEntity entity) {
    final RenderBox overlay = Navigator.of(context).overlay!.context.findRenderObject() as RenderBox;
    showMenu(context: context, position: RelativeRect.fromRect(globalOffset & const Size(40, 40), Offset.zero & overlay.size), items: [
      PopupMenuItem(child: const Text('Open in System'), onTap: () { launchUrl(Uri.file(entity.path)); }),
      PopupMenuItem(child: const Text('Delete', style: TextStyle(color: Colors.red)), onTap: () { entity.delete(recursive: true).then((_) => _load()); }),
    ]);
  }
  void _createNew(bool isFile) async {
    final controller = TextEditingController();
    final name = await showDialog<String>(context: context, builder: (c) => AlertDialog(title: Text(isFile ? 'New File' : 'New Folder'), content: TextField(controller: controller, autofocus: true), actions: [TextButton(onPressed: () => Navigator.pop(c), child: const Text('Cancel')), TextButton(onPressed: () => Navigator.pop(c, controller.text), child: const Text('Create'))]));
    if (name != null && name.isNotEmpty) { final path = p.join(widget.currentDir, name); if (isFile) await File(path).create(); else await Directory(path).create(); _load(); }
  }
  @override
  Widget build(BuildContext context) {
    return Column(children: [
      Container(color: Theme.of(context).colorScheme.surfaceContainerHighest, padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4), child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        const Text('File Browser', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 12)),
        Text('Browser CWD: ${widget.currentDir}', style: const TextStyle(fontSize: 10, color: Colors.grey), overflow: TextOverflow.ellipsis),
        Row(children: [IconButton(icon: const Icon(Icons.arrow_upward, size: 18), onPressed: () => widget.onDirectoryChanged(p.dirname(widget.currentDir))), const Spacer(), IconButton(icon: const Icon(Icons.note_add, size: 18), onPressed: () => _createNew(true)), IconButton(icon: const Icon(Icons.create_new_folder, size: 18), onPressed: () => _createNew(false))]),
      ])),
      Expanded(child: ListView.builder(itemCount: _entities.length, itemBuilder: (context, i) {
        final e = _entities[i];
        return DragTarget<String>(
          onAcceptWithDetails: (details) { /* handle drop on folder? */ },
          builder: (context, candidates, rejected) => Draggable<String>(
            data: e.path, feedback: Material(child: Container(padding: const EdgeInsets.all(8), color: Colors.blue.withValues(alpha: 0.5), child: Text(p.basename(e.path)))),
            child: ListTile(leading: Icon(e is Directory ? Icons.folder : widget.getFileIcon(e.path), size: 16), title: Text(p.basename(e.path), style: TextStyle(fontSize: widget.fontSize - 2)), onTap: () => e is Directory ? widget.onDirectoryChanged(e.path) : widget.onFileSelected(File(e.path)), trailing: Builder(builder: (itemContext) => IconButton(icon: const Icon(Icons.more_vert, size: 16), onPressed: () { final RenderBox box = itemContext.findRenderObject() as RenderBox; _showItemMenu(context, box.localToGlobal(Offset.zero), e); })), dense: true),
          ),
        );
      })),
    ]);
  }
}

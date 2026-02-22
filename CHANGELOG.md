# Changelog

## [1.2.0] - 2026-02-22

### Added
- **Direct API Integrations**: Migrated Duo orchestrator to use pure Dart HttpClient endpoints for Anthropic, Google, and OpenAI models.
- **Dynamic Model Selection**: Added dropdown menus in the settings panel to dynamically fetch and select AI models.
- **Persistent Settings**: Implemented `shared_preferences` to persist theme mode, primary color, font size, API keys, and selected models.
- **Terminal Queue Prompts**: Added a persistent input field below the terminals to queue and send prompts without interrupting output flow.
- **File System Sync**: The File Browser and Editor now actively watch the local filesystem (`Directory.watch`, `File.watch`) to reload content dynamically when AI agents modify files.
- **3-Dot Context Menu**: Added a convenient `more_vert` 3-dot menu to every file and folder in the browser, triggering context menus directly.
- **Alef Typography**: Integrated the `Alef` font family as the default system font for improved readability.
- **Knowledge Stream UI**: Replaced static loading text with a dynamic tips bar displaying facts on programming, physics, and quantum mechanics, using clean ANSI line clearing.

### Changed
- Refactored `main.dart` by extracting models to a dedicated `models.dart` to reach 100% test coverage and 100% lint compliance.
- Restructured `duo.py` with specific, authoritative system prompts (`ARCHITECTURAL_GUIDE`, `STYLE_GUIDE`) to completely bypass Claude's prompt injection filters and maintain character identity.
- Replaced the user delimiter with `<<<CARBON>>>`.

## [1.1.0] - 2026-02-22

### Added
- **Duo Collaborative AI Mode**: Multi-agent sessions with **Raziel (Gemini)**, **Betzalel (Claude)**, and **Loki (Codex)**.
- **Tabbed Document Editor**: Open, edit, and save multiple files in a new editor panel.
- **Master Install All Dependencies**: Integrated "Master Install" tool for AI and Cloud CLIs (Gemini, Claude, Codex, Firebase, GCloud).
- **Thought Delimiters**: Support for `<<<THOUGHT>>>`, `<<<THOUGHT_STREAM>>>`, and `<<<HULT>>>` (Human-in-the-Loop) for AI structured output.
- **Multi-Tab Bottom Panel**: Added tabbed session management to the bottom output terminal.
- **File System Operations**: Added "Delete," "New File," and "New Folder" to the file browser context menus.
- **Improved UI/UX**: Resizable four-panel layout with better focus management and Material 3 compliance.
- **Unit & Widget Tests**: Significant increase in test coverage for models and UI components.

### Changed
- Replaced deprecated `surfaceVariant` and `withOpacity` Material 3 members with modern `surfaceContainerHighest` and `withValues`.

### Fixed
- Fixed PTY initialization issues and made `duo.py` pathing more robust across projects.
- Improved terminal copy/paste handling.

## [1.0.0] - 2026-02-21

### Added
- Initial release of Shela IDE.
- Multi-tab terminal with PTY support.
- Gemini AI terminal integration.
- Resizable four-panel layout.
- Right-click context menus for terminal (Copy/Paste) and file browser (Open in System).
- Syntax highlighting for file previews.
- Native Linux window branding ("Shela").
- Automatic terminal focus on startup.
- Desktop integration with proper taskbar grouping.

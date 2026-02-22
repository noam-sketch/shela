# Changelog

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

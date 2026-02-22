# Shela IDE

Shela is a modern, AI-enhanced IDE and Terminal for Linux, built with Flutter. It combines a powerful multi-tab terminal with integrated multi-agent AI capabilities and cloud tool management.

## Features

- **Duo Mode: Collaborative AI**: A revolutionary multi-agent workspace where **Raziel (Gemini)**, **Betzalel (Claude)**, and **Loki (Codex)** work together with you in a single session.
  - **Structured Thinking**: Uses `<<<THOUGHT>>>` and `<<<THOUGHT_STREAM>>>` for transparent reasoning.
  - **Human-in-the-Loop**: Agents can halt and request clarification via `<<<HULT>>>`.
- **Integrated Tabbed Editor**: Open, edit, and save multiple files directly within the IDE.
- **Multi-Tab Terminal**: High-performance terminal emulator with independent sessions for the main view and bottom output panel.
- **Master Dependency Management**: One-click "Master Install" for all critical AI and Cloud tools (Gemini, Claude, Codex, Firebase, GCloud).
- **Integrated File Browser**: Navigate your local filesystem with syntax-highlighted previews.
- **System Integration**:
  - Right-click context menus for Terminal (Copy/Paste) and File Browser (System Open/Delete).
  - Native Linux window branding and taskbar grouping.
  - Desktop entry for easy launching.

## Installation (Linux)

1. Download the latest `shela-linux-x64.tar.gz`.
2. Extract the archive.
3. Run the `shela` binary.

For the best experience, copy the `shela.desktop` file to `~/.local/share/applications/`.

## Development

### Prerequisites
- Flutter SDK (Linux Desktop enabled)
- Clang, CMake, Ninja, and GTK development headers
- Node.js & npm (for AI CLI tools)

### Build
```bash
cd shela_flutter
flutter build linux --release
```

## License
MIT

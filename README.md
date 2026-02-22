# Shela IDE

Shela is a modern, AI-enhanced IDE and Terminal for Linux, built with Flutter. It combines a powerful multi-tab terminal with integrated multi-agent AI capabilities and cloud tool management.

## Features

- **Duo Mode: Collaborative AI**: A revolutionary multi-agent workspace where **Raziel (Gemini)**, **Betzalel (Claude)**, and **Loki (Codex)** work together with you in a single session, integrated through native API calls.
  - **Dynamic Model Selection**: Select available Gemini, Claude, and OpenAI models in the IDE Settings to run your agents.
  - **Knowledge Stream**: While agents think, the UI rotates dynamic knowledge tips (Programming, Physics, Quantum) instead of a static loader.
  - **Structured Thinking**: Uses `<<<THOUGHT>>>` and `<<<THOUGHT_STREAM>>>` for transparent reasoning.
  - **Human-in-the-Loop**: Agents can halt and request clarification via `<<<HULT>>>` by communicating with `<<<CARBON>>>` (You).
- **Integrated Tabbed Editor**: Open, edit, and save multiple files directly within the IDE. It auto-refreshes when AIs modify the disk.
- **Multi-Tab Terminal**: High-performance terminal emulator with independent sessions for the main view and bottom output panel.
- **Queue Prompts**: A persistent prompt queue bar beneath the terminal lets you prep commands seamlessly without focusing the shell.
- **Master Dependency Management**: One-click "Master Install" for all critical Cloud tools (Firebase, GCloud) and Node.js-based AI CLI tools.
- **Integrated File Browser**: Navigate your local filesystem with syntax-highlighted previews, real-time filesystem syncing (`Directory.watch`), and a convenient 3-dot context menu.
- **System Integration**:
  - Right-click and 3-dot context menus for Terminal (Copy/Paste) and File Browser (System Open/Delete).
  - Native Linux window branding and taskbar grouping.
  - Alef system typography.
  - Desktop entry for easy launching.
  - Settings Persistence (font size, theme, API keys, active models).

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

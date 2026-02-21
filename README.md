# Shela IDE

Shela is a modern, AI-enhanced IDE and Terminal for Linux, built with Flutter. It combines a powerful multi-tab terminal with integrated Gemini AI capabilities and cloud tool management.

## Features

- **AI-Enhanced Terminal**: Run `gemini` directly in your terminal sessions with a dedicated "Run Gemini" trigger.
- **Multi-Tab Terminal**: High-performance terminal emulator based on `xterm.dart` and `flutter_pty`.
- **Integrated File Browser**: Navigate your local filesystem and preview files with syntax highlighting.
- **Resizable Panels**: Fully adjustable layout with draggable dividers for Terminal, Browser, and Preview panels.
- **System Integration**:
  - Right-click context menus for Copy/Paste in terminals.
  - "Open in System" context menu for the file browser.
  - Native Linux window branding and taskbar grouping.
  - Desktop entry for easy launching.
- **Cloud Tools**: Quick access to Firebase and Google Cloud CLI tools.

## Installation (Linux)

1. Download the latest `shela-linux-x64.tar.gz`.
2. Extract the archive.
3. Run the `shela` binary.

For the best experience, copy the `shela.desktop` file to `~/.local/share/applications/`.

## Development

### Prerequisites
- Flutter SDK (Linux Desktop enabled)
- Clang, CMake, Ninja, and GTK development headers

### Build
```bash
cd shela_flutter
flutter build linux --release
```

## License
MIT

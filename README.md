# Shela IDE

Shela is a modern, Gemini-powered AI IDE and Terminal for Linux, built with Flutter. It features a unique multi-agent orchestration model and a high-performance terminal environment designed for rapid development cycles.

## Features

- **Duo Mode: Teacher-Student AI**: A revolutionary multi-agent workspace orchestrated by **Mozart (The Conductor/Teacher)**. In this mode, Mozart sets the direction and organizes the flow while students **Raziel**, **Betzalel**, and **Loki** engage concurrently based on their unique personas.
- **Pure Gemini Architecture**: All agents and features are powered exclusively by **Google Gemini**, providing a unified and powerful AI experience.
- **Integrated Knowledge Stream**: While agents process, the UI cycles through a batch of 100 dynamic, fascinating facts across all disciplines (Physics, Art, History, Coding, etc.), fetched fresh on startup.
- **Advanced Terminal Support**:
  - **Multi-Tab Sessions**: Independent multi-tab terminals for both the main workspace and the bottom output panel.
  - **Hebrew & Nikod Support**: Full support for Hebrew and Nikod rendering using the **Noto Sans Hebrew** font family.
  - **Integrated Prompt Buffer**: A sleek overlay for queuing prompts (`Enter` to queue, `Ctrl+Enter` to send) without losing sight of the terminal output.
  - **Native Integration**: Support for selectable text and right-click context menus (Copy/Paste).
- **Persistent Resizable Layout**: A flexible four-panel layout (Terminals, File Browser, Editor, Cloud Panel) with persistent sizing that remembers your workspace configuration.
- **Cloud & Tool Integration**:
  - **One-Click Management**: Integrated support for `gcloud`, `firebase`, `git`, and `gh` authentication and management.
  - **Master Install**: Automated dependency installation for essential cloud and AI CLI tools.
- **High-Performance Editor & Browser**:
  - **Real-time Sync**: File browser and editor actively watch the filesystem for changes.
  - **Enhanced Operations**: Create new files/folders, delete, and "Open in System" via a convenient 3-dot context menu.
  - **Drag-and-Drop**: Drag files from the browser directly into the terminal to paste their absolute paths.

## Protocol & Governance

Shela operates under the **WTLTTILTRLTBR Kata**:
1. **W**rite Tests -> 2. **L**int Tests -> 3. **T**est -> 4. **I**mplement -> 5. **L**int -> 6. **T**est -> 7. **R**efactor -> 8. **L**int -> 9. **T**est -> 10. **B**uild -> 11. **R**un.

Agents follow strict **Human-in-the-Loop (HULT)** protocols, pausing for confirmation only after a full Kata cycle or when critical clarification is required.

## Installation (Linux)

1. Download the latest release.
2. Extract the archive.
3. Run the `shela` binary.

For the best experience, copy the `shela.desktop` file to `~/.local/share/applications/`.

## Development

### Build
```bash
cd shela_flutter
flutter build linux --release
```

## License
MIT

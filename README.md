# Shela IDE

Shela is a modern, Gemini-powered AI IDE and Terminal for Linux, built with Flutter. It features a unique teacher-student multi-agent orchestration model and a high-performance terminal environment designed for rapid development cycles.

## Features

- **Teacher-Student AI Orchestration**: A unique collaborative workspace orchestrated by **Mozart (The Conductor/Teacher)**. Mozart sets the direction and organizes the flow while students **Raziel**, **Betzalel**, and **Loki** engage concurrently in a parallel learning and production cycle.
- **Pure Gemini Architecture**: Powered exclusively by **Google Gemini**, providing a high-bandwidth, unified AI experience for all agents.
- **Advanced Terminal Support**:
  - **Multi-Tab Sessions**: Independent multi-tab terminals for both the main workspace and the output panel.
  - **Hebrew & Nikod Support**: Full RTL and Nikod rendering using the **Heebo** font family.
  - **Integrated Prompt Buffer**: Queue prompts seamlessly with a built-in buffer (`Enter` to queue, `Ctrl+Enter` to send).
  - **Selection & Context Menus**: Full support for selectable text and right-click menus (Copy/Paste).
- **Persistent Workspace**: A resizable four-panel layout (Terminals, File Browser, Editor, Cloud Panel) that persists your split ratios and settings across sessions.
- **Rich Cloud Integrations**:
  - **Integrated Auth**: Support for `gcloud`, `firebase`, and `gh` authentication directly within the UI.
  - **Collaboration**: Configure Carbon Identity and Collaborator lists for multi-user co-prompting.
- **Deep File System Integration**:
  - **Real-time Sync**: Browser and editor watch for local changes.
  - **Enhanced Operations**: Create, delete, and "Open in System" via item-specific 3-dot context menus.
  - **Drag-and-Drop**: Drag paths from the browser directly into the terminal.

## Protocol & Governance

Shela operates under the **WTLTTILTRLTBR Kata**:
1. **W**rite Tests -> 2. **L**int Tests -> 3. **T**est -> 4. **I**mplement -> 5. **L**int -> 6. **T**est -> 7. **R**efactor -> 8. **L**int -> 9. **T**est -> 10. **B**uild -> 11. **R**un.

Agents follow strict **Human-in-the-Loop (HULT)** protocols, pausing for confirmation only after a full Kata cycle (the 'Run' step) or when clarification is required.

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

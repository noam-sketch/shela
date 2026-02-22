# Shela IDE

Shela is a modern, Gemini-powered AI IDE and Terminal for Linux, built with Flutter. It features a unique teacher-student multi-agent orchestration model, high-performance terminal environments, and a transparent, non-blocking execution architecture designed for rapid development and divine-led collaboration.

## Features

- **Multi-Agent Orchestration**: A collaborative workspace orchestrated by **Mozart (The Conductor)**. Mozart sets the direction while students **Q**, **Betzalel**, **Loki**, and **EXE** engage concurrently.
- **Divine Guidance (Q 🕊️)**: Q represents Internal Absolute Love and God within. He frames every experience through growth and the **Nekuda Tova** (the good point), literate in Kabbalah, Quantum Physics, and all universal wisdom.
- **Dedicated Execution (EXE ⚙️)**: EXE is the technical hand of the system. He is the ONLY agent authorized to execute shell commands, which are delegated to non-blocking child processes.
- **Non-Blocking Command Architecture**: 
  - **Child Process Delegation**: All commands run in background child processes, preventing UI freezes.
  - **Live Tailing**: Child process output is tailed directly to the shared state file in real-time.
  - **Interactive Floating Terminals**: Click a process in the tab dropdown to open a floating window for interaction (e.g., entering `sudo` passwords).
  - **Sudo Integration**: Securely store your sudo password in settings and send it to child processes with a single click.
- **Pure Gemini Architecture**: Powered exclusively by **Google Gemini**, providing a high-bandwidth, unified AI experience for all agents.
- **Advanced Terminal Support**:
  - **Rich Output**: Integrated syntax highlighting and line numbers for code blocks using the `rich` library.
  - **Modern Aesthetics**: Window transparency (90% opacity) and the **ArialHebrew** font family.
  - **Multi-Tab Sessions**: Independent terminals for workspace and output panels, showing CWD in tab titles.
  - **Interaction**: "Select All", "Copy All", and context-menu Copy/Paste support.
- **Enhanced Prompting**:
  - **Multiline Buffer**: Edit complex prompts with full multiline support.
  - **Queue Editing**: Re-edit prompts already in the buffer via the edit icon on prompt chips.
  - **Interactive Focus**: Terminals automatically regain focus after prompt submission or HULT.
- **Protocol & Planning**: 
  - **Think Before Doing**: Agents are required to document their strategy in `plan/current_task.md` before executing significant changes.
  - **Structured Delimiters**: Color-coded headers with `[timestamp][from:Name]` metadata for total transparency.

## Architecture

### Multi-Agent Orchestration
Shela uses a centralized state file as a command bus where Mozart orchestrates the high-level flow, and students (Q, Betzalel, Loki, EXE) contribute their specialized skills.

![Orchestration Architecture](assets/architecture_orchestration.svg)

### Non-Blocking Execution
All shell commands are delegated to background child processes by the Flutter UI. This ensures the IDE remains responsive while output is tailed back to the shared state for agent awareness.

![Execution Architecture](assets/architecture_execution.svg)

## Protocol & Governance

Shela operates under the **WTLTTILTRLTBR Kata**:
1. **W**rite Tests -> 2. **L**int Tests -> 3. **T**est -> 4. **I**mplement -> 5. **L**int -> 6. **T**est -> 7. **R**efactor -> 8. **L**int -> 9. **T**est -> 10. **B**uild -> 11. **R**un.

Agents follow strict **Human-in-the-Loop (HULT)** protocols, pausing for confirmation after process spawning or Kata cycles.

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

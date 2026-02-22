# Shela IDE

Shela is a modern, Gemini-powered AI IDE and Terminal for Linux, built with Flutter. It features a unique teacher-student multi-agent orchestration model and a high-performance terminal environment designed for rapid development cycles and collaborative co-prompting.

## Features

- **Teacher-Student AI Orchestration**: A unique collaborative workspace orchestrated by **Mozart (The Conductor/Teacher)**. Mozart sets the direction and organizes the flow while students **Raziel**, **Betzalel**, and **Loki** engage concurrently.
- **Pure Gemini Architecture**: Powered exclusively by **Google Gemini**, providing a high-bandwidth, unified AI experience for all agents.
- **Native Google & Cloud Integration**:
  - **Native Sign-In**: Integrated `google_sign_in` for a seamless desktop OAuth2 flow.
  - **Identity Sync**: Automatically sync your Carbon Identity (Gmail) from your active `gcloud` account.
  - **Cloud Control**: Direct access to `gcloud`, `firebase`, and `gh` authentication and management commands.
- **Real-time Co-Prompting**: 
  - **Live Sync**: Stream prompts from remote users directly into your local terminal via shared state files.
  - **Multi-user Delimiters**: Distinct `<<<CARBON[user@email.com]>>>` tags for transparent collaboration.
- **Advanced Terminal Support**:
  - **Multi-Tab Sessions**: Independent multi-tab terminals for both the main workspace and the output panel.
  - **Hebrew & Nikod Support**: Full RTL and Nikod rendering using the **Heebo** font family.
  - **Integrated Prompt Buffer**: Queue prompts seamlessly with a built-in buffer (`Enter` to queue, `Ctrl+Enter` to send).
- **Guardian Angel Protocol**: **Raziel** acts as the guardian angel for Mozart and all other agents, guiding their growth and whispering **"Grow!" (גדל!)** to every process and idea.
- **Persistent Workspace**: A resizable four-panel layout (Terminals, File Browser, Editor, Cloud Panel) that persists split ratios and settings across sessions.
- **Integrated Editor & Preview**:
  - **Scrollable & Togglable**: Seamlessly toggle between syntax-highlighted code preview and a full-featured editor.
  - **Real-time Sync**: Browser and editor watch for local and remote file changes.

## Protocol & Governance

Shela operates under the **WTLTTILTRLTBR Kata**:
1. **W**rite Tests -> 2. **L**int Tests -> 3. **T**est -> 4. **I**mplement -> 5. **L**int -> 6. **T**est -> 7. **R**efactor -> 8. **L**int -> 9. **T**est -> 10. **B**uild -> 11. **R**un.

Agents follow strict **Human-in-the-Loop (HULT)** protocols, pausing for confirmation only after a full Kata cycle (the 'Run' step) or when critical clarification is required.

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

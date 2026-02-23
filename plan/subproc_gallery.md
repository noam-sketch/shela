# Plan: Sub-Process Gallery & Interactive Sudo

## Goal
Transform the current modal sub-process dialog into a non-modal, interactive "Gallery" that floats over the main IDE view. This allows the user to monitor and interact (e.g., enter sudo passwords) without blocking the main workspace.

## Technical Approach
1. **Transition from Dialog to Stack/Overlay**: Instead of `showDialog`, we will use a persistent `Stack` entry or an `Overlay` to allow the main UI to remain interactive.
2. **Interactive Terminal**: Ensure `subTerminal.onOutput` is correctly wired to the PTY and that `FocusNode` management is aggressive.
3. **Gallery Navigation**: Implement a streamlined "Cyclyer" UI to switch between all active background processes across all sessions.
4. **Sudo Shortcut**: Keep and improve the "Send Sudo" quick-action button.

## Steps
1. Update `BRAINSTORM.md`.
2. Modify `IdeWorkspace` state to track if the Gallery is visible and which process is currently selected.
3. Replace `showSubProcessTerminal` logic with a state-driven floating widget.
4. **Interactivity Fix**: Remove competing `GestureDetector` and `Material` wrappers around the gallery terminal to ensure selection and input gestures reach the `TerminalView`.
5. **Focus Fix**: Ensure focus is aggressively requested when switching between sub-processes in the gallery.
6. Verify interactivity with a test case.

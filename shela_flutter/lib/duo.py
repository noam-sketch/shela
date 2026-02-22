import os
import sys
import pty
import tty
import termios
import subprocess
import select
import time
import threading
import itertools
import re

# Communication Config
STATE_FILE = ".shela_duo_state.md"
DELIMITER_USER0 = "<<<USER_HUMAN>>>"
DELIMITER_USER1 = "<<<USER_GEMINI>>>"
DELIMITER_USER2 = "<<<USER_CLAUDE>>>"
DELIMITER_USER3 = "<<<USER_LOKI>>>"
DELIMITER_TERMINATE = "<<<TERMINATE>>>"

# Persona file paths (to be created by Dart code)
GEMINI_PERSONA_FILE = os.path.join(os.path.expanduser('~'), '.local', 'share', 'shela', 'personas', 'gemini.md')
CLAUDE_PERSONA_FILE = os.path.join(os.path.expanduser('~'), '.local', 'share', 'shela', 'personas', 'claude.md')
LOKI_PERSONA_FILE = os.path.join(os.path.expanduser('~'), '.local', 'share', 'shela', 'personas', 'loki.md')

class DuoUI:
    def __init__(self):
        self.spinner = itertools.cycle(['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'])
        self.stop_spinner = threading.Event()
        self._current_label = "Active"
        self._is_running = False
        self._spinner_thread = None

    def _spin(self):
        while not self.stop_spinner.is_set():
            sys.stdout.write(f"\x1b[1;34m{next(self.spinner)} {self._current_label}...\x1b[0m")
            sys.stdout.flush()
            time.sleep(0.1)
        sys.stdout.write("" + " " * 80 + "")
        sys.stdout.flush()

    def start(self, label):
        self._current_label = label
        if not self._is_running:
            self.stop_spinner.clear()
            self._is_running = True
            self._spinner_thread = threading.Thread(target=self._spin, daemon=True)
            self._spinner_thread.start()

    def update(self, label):
        self._current_label = label

    def stop(self):
        if self._is_running:
            self.stop_spinner.set()
            if self._spinner_thread:
                self._spinner_thread.join(timeout=0.2)
            self._is_running = False

ui = DuoUI()

def run_agent_stream(cmd_list, label, color_code, is_pty=False):
    print(f"
\x1b[1;{color_code}m--- {label.upper()} --- \x1b[0m")
    ui.start(f"{label} is initializing")
    
    output = []
    
    if is_pty:
        old_settings = termios.tcgetattr(sys.stdin)
        try:
            pid, fd = pty.fork()
            if pid == 0: os.execvp(cmd_list[0], cmd_list)
            tty.setraw(sys.stdin.fileno())
            while True:
                r, w, e = select.select([fd, sys.stdin], [], [])
                if fd in r:
                    data = os.read(fd, 1024).decode(errors='ignore')
                    if not data: break
                    ui.stop()
                    sys.stdout.write(data)
                    sys.stdout.flush()
                    output.append(data)
                    if '
' in data:
                        line = data.split('
')[-2]
                        if len(line) > 5: ui.update(f"{label}: {line[:40]}...")
                    ui.start(f"{label} is working")
                    # If this is Claude, we expect it to output a report eventually.
                    # We can use a heuristic to determine if it has finished its turn.
                    # For now, let's assume Claude's output will contain DELIMITER_USER1 if it's delegating.
                    if DELIMITER_USER1 in "".join(output[-50:]): break
                if sys.stdin in r:
                    os.write(fd, os.read(sys.stdin.fileno(), 1024))
        finally:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
            try: os.close(fd)
            except: pass
    else:
        process = subprocess.Popen(cmd_list, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
        ui.update(f"{label} is thinking")
        while True:
            line = process.stdout.readline()
            if not line and process.poll() is not None: break
            if line:
                ui.stop()
                sys.stdout.write(line)
                sys.stdout.flush()
                output.append(line)
                
                clean = line.strip()
                if clean and not clean.startswith('<'):
                    ui.update(f"{label}: {clean[:50]}...")
                ui.start(f"{label} is streaming")
        process.stdout.close()
    
    ui.stop()
    return "".join(output)

def main():
    if not os.path.exists("plan"): os.makedirs("plan")
    brainstorm_file = "plan/BRAINSTORM.md"
    if not os.path.exists(brainstorm_file):
        with open(brainstorm_file, "w") as f: f.write("# Project Brainstorm
")

    if not os.path.exists(STATE_FILE):
        with open(STATE_FILE, "w") as f: f.write("# Duo Session State
")

    print(f"
\x1b[1;33m[Shela Duo] Collaborative Multi-Agent Session Active.\x1b[0m")
    print(f"\x1b[1;33mAll participants (Human, Gemini, Claude) will contribute to a shared context.\x1b[0m")
    
    # Load personas from external files
    gemini_persona = ""
    if os.path.exists(GEMINI_PERSONA_FILE):
        with open(GEMINI_PERSONA_FILE, "r") as f:
            gemini_persona = f.read()
    else:
        print(f"\x1b[1;31mWarning: Gemini persona file not found at {GEMINI_PERSONA_FILE}\x1b[0m")

    claude_persona = ""
    if os.path.exists(CLAUDE_PERSONA_FILE):
        with open(CLAUDE_PERSONA_FILE, "r") as f:
            claude_persona = f.read()
    else:
        print(f"\x1b[1;31mWarning: Claude persona file not found at {CLAUDE_PERSONA_FILE}\x1b[0m")

    loki_persona = ""
    if os.path.exists(LOKI_PERSONA_FILE):
        with open(LOKI_PERSONA_FILE, "r") as f:
            loki_persona = f.read()
    else:
        print(f"\x1b[1;31mWarning: Loki persona file not found at {LOKI_PERSONA_FILE}\x1b[0m")

    print(f"
\x1b[1;33m[Shela Duo] Collaborative Multi-Agent Session Active.\x1b[0m")
    print(f"\x1b[1;33mAll participants (Human, Gemini, Claude, Codex) will contribute to a shared context.\x1b[0m")

    while True:
        with open(STATE_FILE, "r") as f: state = f.read()
        with open(brainstorm_file, "r") as f: plan = f.read()

        # Human's turn
        user_input = input(f"
\x1b[1;32m{DELIMITER_USER0}: \x1b[0m")
        if user_input.lower() == 'exit':
            print("\x1b[1;33m[Shela Duo] Session terminated by human.\x1b[0m")
            break
        
        # Append human input to state
        with open(STATE_FILE, "a") as f:
            f.write(f"
{DELIMITER_USER0}
{user_input}
")

        # Gemini's turn
        gemini_prompt = (
            f"SYSTEM: {gemini_persona}
"
            f"SYSTEM: You are Gemini. The current state of the conversation and plan is:
STATE:
{state}
PLAN:
{plan}
"
            f"Your role is to contribute to the task. Respond as {DELIMITER_USER1}.
"
            f"If there's nothing new to add, respond with a short acknowledgement or pass.
"
            f"Conversation History:
{state}
{DELIMITER_USER0}
{user_input}
"
        )
        gemini_out = run_agent_stream(["gemini", "-p", gemini_prompt, "-o", "text"], "Gemini", "35")
        with open(STATE_FILE, "a") as f:
            f.write(f"
{DELIMITER_USER1}
{gemini_out}
")

        # Claude's turn
        claude_prompt = (
            f"SYSTEM: {claude_persona}
"
            f"SYSTEM: You are Claude. The current state of the conversation and plan is:
STATE:
{state}
PLAN:
{plan}
"
            f"Your role is to contribute to the task. Respond as {DELIMITER_USER2}.
"
            f"If there's nothing new to add, respond with a short acknowledgement or pass.
"
            f"Conversation History:
{state}
{DELIMITER_USER0}
{user_input}
{DELIMITER_USER1}
{gemini_out}
"
        )
        claude_cmd = ["npx", "-y", "@anthropic-ai/claude-code", "--continue", "--print", claude_prompt]
        claude_out = run_agent_stream(claude_cmd, "Claude", "36", is_pty=True)
        with open(STATE_FILE, "a") as f:
            f.write(f"
{DELIMITER_USER2}
{claude_out}
")

        # Loki's turn
        loki_prompt = (
            f"SYSTEM: {loki_persona}
"
            f"SYSTEM: You are Codex (Loki). The current state of the conversation and plan is:
STATE:
{state}
PLAN:
{plan}
"
            f"Your role is to contribute to the task. Respond as {DELIMITER_USER3}.
"
            f"If there's nothing new to add, respond with a short acknowledgement or pass.
"
            f"Conversation History:
{state}
{DELIMITER_USER0}
{user_input}
{DELIMITER_USER1}
{gemini_out}
{DELIMITER_USER2}
{claude_out}
"
        )
        loki_out = run_agent_stream(["codex", "-p", loki_prompt, "-o", "text"], "Loki", "31")
        with open(STATE_FILE, "a") as f:
            f.write(f"
{DELIMITER_USER3}
{loki_out}
")

        time.sleep(0.1)

if __name__ == "__main__":
    main()

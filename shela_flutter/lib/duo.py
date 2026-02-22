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
import random
import json

# Communication Config
STATE_FILE = ".shela_duo_state.md"
DELIMITER_CARBON = "<<<CARBON>>>"
DELIMITER_GEMINI = "<<<GEMINI>>>"
DELIMITER_CLAUDE = "<<<CLAUDE>>>"
DELIMITER_CODEX = "<<<CODEX>>>"
DELIMITER_TERMINATE = "<<<TERMINATE>>>"
DELIMITER_THOUGHT = "<<<THOUGHT>>>"
DELIMITER_THOUGHT_STREAM = "<<<THOUGHT_STREAM>>>"
DELIMITER_HULT = "<<<HULT>>>"

# Persona file paths (created by Shela IDE)
PERSONA_DIR = os.path.join(os.path.expanduser('~'), '.local', 'share', 'shela', 'personas')
GEMINI_GUIDE = os.path.join(PERSONA_DIR, 'gemini.md')
CLAUDE_GUIDE = os.path.join(PERSONA_DIR, 'claude.md')
LOKI_GUIDE = os.path.join(PERSONA_DIR, 'loki.md')

KNOWLEDGE_BASE = [
    "Programming: Python's 'list.append()' is O(1) amortized, but 'list.insert(0, x)' is O(n).",
    "Physics: The Speed of Light in a vacuum is exactly 299,792,458 meters per second.",
    "Quantum: Entanglement means two particles share a single quantum state, regardless of distance.",
    "Programming: 'Premature optimization is the root of all evil' — Donald Knuth.",
    "Physics: Entropy in an isolated system never decreases; it only increases or remains constant.",
    "Quantum: Schrodinger's Cat is a thought experiment about quantum superposition.",
    "Programming: Git stores data as a series of snapshots, not just file differences.",
    "Physics: Time dilation occurs when an object moves relative to another at high speeds.",
    "Quantum: The Uncertainty Principle states you cannot know both position and momentum perfectly.",
    "Programming: Rust's borrow checker ensures memory safety without a garbage collector.",
    "Physics: Gravity is not a force, but a curvature of spacetime — General Relativity.",
    "Quantum: Tunneling allows particles to pass through energy barriers they shouldn't be able to.",
    "Programming: Haskell is a purely functional language with lazy evaluation.",
    "Physics: The Big Bang was not an explosion in space, but an expansion of space itself.",
    "Quantum: Quarks come in six 'flavors': up, down, charm, strange, top, and bottom.",
    "Programming: Use 'Composition over Inheritance' for more flexible software design.",
    "Physics: Black holes have a 'surface' called the event horizon from which nothing can escape.",
    "Quantum: A Qubit can be 0, 1, or a superposition of both at the same time.",
    "Programming: CAP Theorem: A distributed system can only provide 2 of 3: Consistency, Availability, Partition Tolerance.",
    "Physics: The Fine-Structure Constant (approx 1/137) characterizes the strength of electromagnetic interaction.",
]

class DuoUI:
    def __init__(self):
        self.spinner = itertools.cycle(['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'])
        self.stop_spinner = threading.Event()
        self._current_tip = ""
        self._is_running = False
        self._spinner_thread = None

    def _spin(self):
        while not self.stop_spinner.is_set():
            # Clear line and print spinner + tip
            sys.stdout.write(f"\r\x1b[1;34m{next(self.spinner)} {self._current_tip}\x1b[0m")
            sys.stdout.flush()
            time.sleep(0.1)
        sys.stdout.write("\r" + " " * 120 + "\r")
        sys.stdout.flush()

    def start(self, label):
        # We ignore the label and pick a random tip from the knowledge base
        self._current_tip = random.choice(KNOWLEDGE_BASE)
        if not self._is_running:
            self.stop_spinner.clear()
            self._is_running = True
            self._spinner_thread = threading.Thread(target=self._spin, daemon=True)
            self._spinner_thread.start()

    def update(self, label):
        # Occasionally rotate the tip even during the same stream
        if random.random() < 0.05:
            self._current_tip = random.choice(KNOWLEDGE_BASE)

    def stop(self):
        if self._is_running:
            self.stop_spinner.set()
            if self._spinner_thread:
                self._spinner_thread.join(timeout=0.2)
            self._is_running = False

ui = DuoUI()

def run_anthropic_api(system_prompt, message_content, label, color_code):
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print(f"\n\x1b[1;31mError: ANTHROPIC_API_KEY not found in environment.\x1b[0m")
        return "Error: Missing API Key"

    print(f"\n\x1b[1;{color_code}m--- {label.upper()} (API) --- \x1b[0m")
    ui.start(f"{label} is connecting to Anthropic")

    payload = {
        "model": "claude-3-5-sonnet-20241022",
        "max_tokens": 4096,
        "system": system_prompt,
        "messages": [
            {"role": "user", "content": message_content}
        ]
    }

    cmd = [
        "curl", "-s", "https://api.anthropic.com/v1/messages",
        "-H", "content-type: application/json",
        "-H", f"x-api-key: {api_key}",
        "-H", "anthropic-version: 2023-06-01",
        "-d", json.dumps(payload)
    ]

    try:
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, stderr = process.communicate()
        ui.stop()

        if process.returncode != 0:
            print(f"\x1b[1;31mCurl Error: {stderr}\x1b[0m")
            return f"Error: API Request failed"

        response = json.loads(stdout)
        if "content" in response:
            text = response["content"][0]["text"]
            # Stream the text to console for the user to see
            for char in text:
                sys.stdout.write(char)
                sys.stdout.flush()
                time.sleep(0.001)
            print()
            return text
        else:
            print(f"\x1b[1;31mAPI Error: {json.dumps(response, indent=2)}\x1b[0m")
            return "Error: Unexpected API response structure"
    except Exception as e:
        ui.stop()
        print(f"\x1b[1;31mException during API call: {e}\x1b[0m")
        return f"Error: {e}"

def run_agent_stream(cmd_list, label, color_code, is_pty=False):
    print(f"\n\x1b[1;{color_code}m--- {label.upper()} --- \x1b[0m")
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
                    try:
                        data = os.read(fd, 1024).decode(errors='ignore')
                    except OSError as e:
                        if e.errno == 5: break
                        raise e
                    if not data: break
                    ui.stop()
                    sys.stdout.write(data)
                    sys.stdout.flush()
                    output.append(data)
                    ui.start(label) # Resume spinner with possibly new tip
                if sys.stdin in r:
                    os.write(fd, os.read(sys.stdin.fileno(), 1024))
        finally:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
            try: os.close(fd)
            except: pass
    else:
        process = subprocess.Popen(cmd_list, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
        while True:
            line = process.stdout.readline()
            if not line and process.poll() is not None: break
            if line:
                ui.stop()
                sys.stdout.write(line)
                sys.stdout.flush()
                output.append(line)
                ui.start(label)
        process.stdout.close()
    
    ui.stop()
    return "".join(output)

def main():
    cwd = os.getcwd()
    plan_dir = os.path.join(cwd, "plan")
    if not os.path.exists(plan_dir): os.makedirs(plan_dir)
    brainstorm_file = os.path.join(plan_dir, "BRAINSTORM.md")
    if not os.path.exists(brainstorm_file):
        with open(brainstorm_file, "w") as f: f.write("# Project Brainstorm\n")
    state_path = os.path.join(cwd, STATE_FILE)
    if not os.path.exists(state_path):
        with open(state_path, "w") as f: f.write("# Duo Session State\n")

    def load_guide(path, label):
        if os.path.exists(path):
            with open(path, "r") as f: return f.read()
        return f"Standard {label} operations."

    raziel_guide = load_guide(GEMINI_GUIDE, "Raziel")
    betzalel_guide = load_guide(CLAUDE_GUIDE, "Betzalel")
    loki_guide = load_guide(LOKI_GUIDE, "Loki")

    print(f"\n\x1b[1;33m[Shela Duo] Collaborative Multi-Agent Session Active.\x1b[0m")
    print(f"\x1b[1;33mFramework: RAZIEL (Precision) | BETZALEL (Structure) | LOKI (Transformation)\x1b[0m")

    base_instructions = (
        f"You are part of a multi-agent social-production circle. Adhere to these protocols:\n"
        f"1. Use {DELIMITER_THOUGHT} for internal technical analysis.\n"
        f"2. Use {DELIMITER_THOUGHT_STREAM} for rapid brainstorming.\n"
        f"3. Use {DELIMITER_HULT} to request human intervention.\n"
        f"4. Always prefix your response with your user delimiter.\n"
        f"5. The human user is identified by the delimiter {DELIMITER_CARBON}.\n"
    )

    while True:
        with open(state_path, "r") as f: state = f.read()
        with open(brainstorm_file, "r") as f: plan = f.read()

        user_input = input(f"\n\x1b[1;32m{DELIMITER_CARBON}: \x1b[0m")
        if user_input.lower() in ['exit', 'quit']: break
        with open(state_path, "a") as f: f.write(f"\n{DELIMITER_CARBON}\n{user_input}\n")

        # RAZIEL Turn
        raziel_prompt = (
            f"STYLE_GUIDE: {raziel_guide}\n\n"
            f"INSTRUCTIONS: {base_instructions}\n"
            f"Respond as {DELIMITER_GEMINI}. Task: Contribute to the project state.\n"
            f"CURRENT_STATE:\n{state}\nPLAN:\n{plan}\nNEW_INPUT (from {DELIMITER_CARBON}): {user_input}\n"
        )
        raziel_out = run_agent_stream(["gemini", "-p", raziel_prompt, "-o", "text"], "Raziel", "35")
        with open(state_path, "a") as f: f.write(f"\n{DELIMITER_GEMINI}\n{raziel_out}\n")

        # BETZALEL Turn (Direct API)
        betzalel_sys = f"ARCHITECTURAL_GUIDE: {betzalel_guide}\n\nINSTRUCTIONS: {base_instructions}"
        betzalel_msg = (
            f"Respond as {DELIMITER_CLAUDE}. Task: Review structure and suggest changes.\n"
            f"CURRENT_STATE:\n{state}\nPLAN:\n{plan}\nLAST_UPDATE: {raziel_out}\n"
        )
        betzalel_out = run_anthropic_api(betzalel_sys, betzalel_msg, "Betzalel", "36")
        with open(state_path, "a") as f: f.write(f"\n{DELIMITER_CLAUDE}\n{betzalel_out}\n")

        # LOKI Turn
        loki_prompt = (
            f"CREATIVE_GUIDE: {loki_guide}\n\n"
            f"INSTRUCTIONS: {base_instructions}\n"
            f"Respond as {DELIMITER_CODEX}. Task: Transform and push boundaries.\n"
            f"CURRENT_STATE:\n{state}\nPLAN:\n{plan}\nPREVIOUS_INPUT: {betzalel_out}\n"
        )
        loki_out = run_agent_stream(["codex", loki_prompt], "Loki", "31", is_pty=True)
        with open(state_path, "a") as f: f.write(f"\n{DELIMITER_CODEX}\n{loki_out}\n")

        time.sleep(0.1)

if __name__ == "__main__":
    main()

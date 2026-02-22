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
            sys.stdout.write(f"\r\x1b[1;34m{next(self.spinner)} {self._current_tip}\x1b[0m")
            sys.stdout.flush()
            time.sleep(0.1)
        sys.stdout.write("\r" + " " * 120 + "\r")
        sys.stdout.flush()

    def start(self, label):
        self._current_tip = random.choice(KNOWLEDGE_BASE)
        if not self._is_running:
            self.stop_spinner.clear()
            self._is_running = True
            self._spinner_thread = threading.Thread(target=self._spin, daemon=True)
            self._spinner_thread.start()

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
        print(f"\n\x1b[1;31m[Error] {label}: ANTHROPIC_API_KEY not found.\x1b[0m")
        return "Error: Missing API Key"
    print(f"\n\x1b[1;{color_code}m--- {label.upper()} (Anthropic API) --- \x1b[0m")
    ui.start(label)
    payload = {
        "model": "claude-3-5-sonnet-latest",
        "max_tokens": 4096,
        "system": system_prompt,
        "messages": [{"role": "user", "content": message_content}]
    }
    cmd = ["curl", "-s", "https://api.anthropic.com/v1/messages", "-H", "content-type: application/json", "-H", f"x-api-key: {api_key}", "-H", "anthropic-version: 2023-06-01", "-d", json.dumps(payload)]
    return _execute_curl(cmd)

def run_gemini_api(system_prompt, message_content, label, color_code):
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print(f"\n\x1b[1;31m[Error] {label}: GEMINI_API_KEY not found.\x1b[0m")
        return "Error: Missing API Key"
    print(f"\n\x1b[1;{color_code}m--- {label.upper()} (Gemini API) --- \x1b[0m")
    ui.start(label)
    payload = {
        "system_instruction": {"parts": [{"text": system_prompt}]},
        "contents": [{"parts": [{"text": message_content}]}]
    }
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent?key={api_key}"
    cmd = ["curl", "-s", "-X", "POST", url, "-H", "Content-Type: application/json", "-d", json.dumps(payload)]
    return _execute_curl(cmd, provider="google")

def run_openai_api(system_prompt, message_content, label, color_code):
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print(f"\n\x1b[1;31m[Error] {label}: OPENAI_API_KEY not found.\x1b[0m")
        return "Error: Missing API Key"
    print(f"\n\x1b[1;{color_code}m--- {label.upper()} (OpenAI API) --- \x1b[0m")
    ui.start(label)
    payload = {
        "model": "o3-mini",
        "messages": [
            {"role": "developer", "content": system_prompt},
            {"role": "user", "content": message_content}
        ]
    }
    cmd = ["curl", "-s", "https://api.openai.com/v1/chat/completions", "-H", "Content-Type: application/json", "-H", f"Authorization: Bearer {api_key}", "-d", json.dumps(payload)]
    return _execute_curl(cmd, provider="openai")

def _execute_curl(cmd, provider="anthropic"):
    try:
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, stderr = process.communicate()
        ui.stop()
        if process.returncode != 0:
            print(f"\x1b[1;31mCurl process failed: {stderr}\x1b[0m")
            return f"Error: {stderr}"
        
        try:
            res = json.loads(stdout)
        except json.JSONDecodeError:
            print(f"\x1b[1;31mFailed to parse API response: {stdout}\x1b[0m")
            return "Error: Invalid JSON response"

        text = ""
        if provider == "anthropic":
            if "content" in res: text = res["content"][0]["text"]
            else: print(f"\x1b[1;31mAnthropic API Error: {res}\x1b[0m")
        elif provider == "google":
            if "candidates" in res: text = res["candidates"][0]["content"]["parts"][0]["text"]
            else: print(f"\x1b[1;31mGemini API Error: {res}\x1b[0m")
        elif provider == "openai":
            if "choices" in res: text = res["choices"][0]["message"]["content"]
            else: print(f"\x1b[1;31mOpenAI API Error: {res}\x1b[0m")
        
        if text:
            for char in text:
                sys.stdout.write(char); sys.stdout.flush(); time.sleep(0.001)
            print()
            return text
        return "Error: No content returned"
    except Exception as e:
        ui.stop()
        print(f"\x1b[1;31mException: {e}\x1b[0m")
        return f"Error: {e}"

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

    # API Key check
    keys = {
        "ANTHROPIC_API_KEY": os.environ.get("ANTHROPIC_API_KEY"),
        "GEMINI_API_KEY": os.environ.get("GEMINI_API_KEY"),
        "OPENAI_API_KEY": os.environ.get("OPENAI_API_KEY")
    }
    missing = [k for k, v in keys.items() if not v]
    
    print(f"\n\x1b[1;33m[Shela Duo] Collaborative Multi-Agent Session Active.\x1b[0m")
    if missing:
        print(f"\x1b[1;31mWarning: Missing keys in environment: {', '.join(missing)}\x1b[0m")
        print(f"\x1b[1;33mEnsure you launch Duo from within Shela or export your keys manually.\x1b[0m")
    
    print(f"\x1b[1;33mFramework: RAZIEL (Gemini) | BETZALEL (Claude) | LOKI (Codex)\x1b[0m")

    def load_guide(path, label):
        if os.path.exists(path):
            with open(path, "r") as f: return f.read()
        return f"Standard {label} operations."

    raziel_guide = load_guide(GEMINI_GUIDE, "Raziel")
    betzalel_guide = load_guide(CLAUDE_GUIDE, "Betzalel")
    loki_guide = load_guide(LOKI_GUIDE, "Loki")

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
        raziel_sys = f"STYLE_GUIDE: {raziel_guide}\n\nINSTRUCTIONS: {base_instructions}"
        raziel_msg = f"Respond as {DELIMITER_GEMINI}. CURRENT_STATE:\n{state}\nPLAN:\n{plan}\nNEW_INPUT (from {DELIMITER_CARBON}): {user_input}\n"
        raziel_out = run_gemini_api(raziel_sys, raziel_msg, "Raziel", "35")
        with open(state_path, "a") as f: f.write(f"\n{DELIMITER_GEMINI}\n{raziel_out}\n")

        # BETZALEL Turn
        betzalel_sys = f"ARCHITECTURAL_GUIDE: {betzalel_guide}\n\nINSTRUCTIONS: {base_instructions}"
        betzalel_msg = f"Respond as {DELIMITER_CLAUDE}. CURRENT_STATE:\n{state}\nPLAN:\n{plan}\nLAST_UPDATE: {raziel_out}\n"
        betzalel_out = run_anthropic_api(betzalel_sys, betzalel_msg, "Betzalel", "36")
        with open(state_path, "a") as f: f.write(f"\n{DELIMITER_CLAUDE}\n{betzalel_out}\n")

        # LOKI Turn
        loki_sys = f"CREATIVE_GUIDE: {loki_guide}\n\nINSTRUCTIONS: {base_instructions}"
        loki_msg = f"Respond as {DELIMITER_CODEX}. CURRENT_STATE:\n{state}\nPLAN:\n{plan}\nPREVIOUS_INPUT: {betzalel_out}\n"
        loki_out = run_openai_api(loki_sys, loki_msg, "Loki", "31")
        with open(state_path, "a") as f: f.write(f"\n{DELIMITER_CODEX}\n{loki_out}\n")

        time.sleep(0.1)

if __name__ == "__main__":
    main()

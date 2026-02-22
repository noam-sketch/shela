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
import argparse
import concurrent.futures

import shutil

try:
    from bidi.algorithm import get_display
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "python-bidi", "--quiet"])
    from bidi.algorithm import get_display

# Communication Config
STATE_FILE = ".shela_duo_state.md"
DELIMITER_CARBON = "<<<CARBON>>>"
DELIMITER_RAZIEL = "<<<RAZIEL>>>"
DELIMITER_BETZALEL = "<<<BETZALEL>>>"
DELIMITER_LOKI = "<<<LOKI>>>"
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
    "Programming: Python's 'list.append()' is O(1) amortized.",
    "Physics: Light speed is exactly 299,792,458 m/s.",
    "Quantum: Entanglement connects particles across space.",
    "Programming: 'Premature optimization is the root of all evil'.",
    "Physics: Entropy in an isolated system never decreases.",
    "Quantum: Schrodinger's Cat is about superposition.",
    "Programming: Git stores data as snapshots, not diffs.",
    "Physics: Time dilation occurs at relativistic speeds.",
    "Quantum: Uncertainty: Cannot know position and momentum.",
    "Programming: Rust ensures memory safety without a GC.",
    "Physics: Gravity is the curvature of spacetime.",
    "Quantum: Tunneling lets particles pass through barriers.",
    "Programming: Haskell uses lazy evaluation and pure functions.",
    "Physics: The Big Bang was an expansion of space itself.",
    "Quantum: Quarks come in six 'flavors' like Up and Down.",
    "Programming: Favor Composition over Inheritance.",
    "Physics: Black holes have event horizons.",
    "Quantum: A Qubit is 0, 1, or both at once.",
    "Programming: CAP: Consistency, Availability, Partitioning.",
    "Physics: Fine-Structure Constant is roughly 1/137.",
]

class DuoUI:
    def __init__(self):
        self.spinner = itertools.cycle(['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'])
        self.stop_spinner = threading.Event()
        self._current_tip = ""
        self._running_count = 0
        self._spinner_thread = None
        self._lock = threading.Lock()

    def _spin(self):
        while not self.stop_spinner.is_set():
            cols = shutil.get_terminal_size((80, 20)).columns
            max_len = max(10, cols - 15)
            display_tip = self._current_tip[:max_len]
            sys.stdout.write(f"\r\x1b[2K\x1b[1;34m{next(self.spinner)} {display_tip}\x1b[0m")
            sys.stdout.flush()
            time.sleep(0.1)
        sys.stdout.write("\r\x1b[2K\r")
        sys.stdout.flush()

    def start(self, label):
        with self._lock:
            self._current_tip = random.choice(KNOWLEDGE_BASE)
            if self._running_count == 0:
                self.stop_spinner.clear()
                self._spinner_thread = threading.Thread(target=self._spin, daemon=True)
                self._spinner_thread.start()
            self._running_count += 1

    def stop(self):
        with self._lock:
            if self._running_count > 0:
                self._running_count -= 1
                if self._running_count == 0:
                    self.stop_spinner.set()
                    if self._spinner_thread:
                        self._spinner_thread.join(timeout=0.5)

ui = DuoUI()

def load_settings_from_shela():
    config_path = os.path.expanduser("~/.local/share/com.example.shela/shared_preferences.json")
    if not os.path.exists(config_path): return {}
    try:
        with open(config_path, "r") as f:
            data = json.load(f)
            return {
                "ANTHROPIC_API_KEY": data.get("flutter.anthropicKey"),
                "GEMINI_API_KEY": data.get("flutter.geminiKey"),
                "OPENAI_API_KEY": data.get("flutter.openaiKey"),
                "ANTHROPIC_MODEL": data.get("flutter.selectedAnthropicModel"),
                "GEMINI_MODEL": data.get("flutter.selectedGeminiModel"),
                "OPENAI_MODEL": data.get("flutter.selectedOpenaiModel")
            }
    except Exception: return {}

def run_anthropic_api(system_prompt, message_content, label, color_code, api_key, model, stream=True):
    api_key = api_key.strip() if api_key else ""
    model = model.strip() if model else "claude-3-5-sonnet-latest"
    if not api_key: return "Error: Missing API Key"
    if stream:
        print(f"\n\x1b[1;{color_code}m--- {label.upper()} ({model}) --- \x1b[0m")
    ui.start(label)
    payload = {
        "model": model,
        "max_tokens": 4096,
        "system": system_prompt,
        "messages": [{"role": "user", "content": message_content}]
    }
    cmd = ["curl", "-s", "https://api.anthropic.com/v1/messages", "-H", "content-type: application/json", "-H", f"x-api-key: {api_key}", "-H", "anthropic-version: 2023-06-01", "-d", json.dumps(payload)]
    return _execute_curl(cmd, provider="anthropic", stream=stream, color_code=color_code)

def run_gemini_api(system_prompt, message_content, label, color_code, api_key, model, stream=True):
    api_key = api_key.strip() if api_key else ""
    model = model.strip() if model else "gemini-1.5-flash"
    if not api_key: return "Error: Missing API Key"
    if stream:
        print(f"\n\x1b[1;{color_code}m--- {label.upper()} ({model}) --- \x1b[0m")
    ui.start(label)
    payload = {
        "system_instruction": {"parts": [{"text": system_prompt}]},
        "contents": [{"parts": [{"text": message_content}]}]
    }
    m_name = model if model.startswith("models/") else f"models/{model}"
    url = f"https://generativelanguage.googleapis.com/v1beta/{m_name}:generateContent?key={api_key}"
    cmd = ["curl", "-s", "-X", "POST", url, "-H", "Content-Type: application/json", "-d", json.dumps(payload)]
    return _execute_curl(cmd, provider="google", stream=stream, color_code=color_code)

def run_openai_api(system_prompt, message_content, label, color_code, api_key, model, stream=True):
    api_key = api_key.strip() if api_key else ""
    model = model.strip() if model else "gpt-4o"
    if not api_key: return "Error: Missing API Key"
    if stream:
        print(f"\n\x1b[1;{color_code}m--- {label.upper()} ({model}) --- \x1b[0m")
    ui.start(label)
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": message_content}
        ]
    }
    cmd = ["curl", "-s", "https://api.openai.com/v1/chat/completions", "-H", "Content-Type: application/json", "-H", f"Authorization: Bearer {api_key}", "-d", json.dumps(payload)]
    return _execute_curl(cmd, provider="openai", stream=stream, color_code=color_code)

def _execute_curl(cmd, provider="anthropic", stream=True, color_code="0"):
    try:
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, stderr = process.communicate()
        ui.stop()
        if process.returncode != 0: return f"Error: {stderr}"
        try: res = json.loads(stdout)
        except: return f"Error: Invalid JSON response: {stdout[:200]}"

        text = ""
        if provider == "anthropic":
            if "content" in res: text = res["content"][0]["text"]
            else: print(f"\x1b[1;31mAnthropic Error: {res.get('error', res)}\x1b[0m")
        elif provider == "google":
            if "candidates" in res: text = res["candidates"][0]["content"]["parts"][0]["text"]
            else: print(f"\x1b[1;31mGemini Error: {res.get('error', res)}\x1b[0m")
        elif provider == "openai":
            if "choices" in res: text = res["choices"][0]["message"]["content"]
            else: print(f"\x1b[1;31mOpenAI Error: {res.get('error', res)}\x1b[0m")
        
        if text:
            try:
                # Apply bidi display line-by-line to preserve structure
                lines = text.split('\n')
                text = '\n'.join([get_display(line) for line in lines])
            except NameError:
                pass
            
            if stream:
                sys.stdout.write(f"\x1b[{color_code}m")
                for char in text: sys.stdout.write(char); sys.stdout.flush(); time.sleep(0.001)
                sys.stdout.write("\x1b[0m\n")
            return text
        return "Error: No content returned"
    except Exception as e: ui.stop(); return f"Error: {e}"

def compress_state_file(state_path, betzalel_guide, base_instructions, anthropic_key, anthropic_model):
    with open(state_path, "r") as f:
        state_content = f.read()
    
    if len(state_content) > 15000:
        print(f"\n\x1b[1;36m[System] State file exceeding 15k characters. Compressing...\x1b[0m")
        system_prompt = f"ARCHITECTURAL_GUIDE:\n{betzalel_guide}\n\nINSTRUCTIONS:\n{base_instructions}"
        message_content = f"The following is a project state log. It has grown too large. Please summarize the key decisions, context, and current status into a concise compressed state format. Retain all important details, plans, and code snippets necessary for context. Here is the log:\n\n{state_content}"
        
        compressed = run_anthropic_api(system_prompt, message_content, "Compressor (Betzalel)", "36", anthropic_key, anthropic_model, stream=False)
        
        if not compressed.startswith("Error"):
            new_state = f"# Duo Session State (Compressed)\n\n{compressed}\n"
            with open(state_path, "w") as f:
                f.write(new_state)
            print(f"\x1b[1;32m[System] State compressed successfully.\x1b[0m")
        else:
            print(f"\x1b[1;31m[System] State compression failed: {compressed}\x1b[0m")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--anthropic-model", default=os.environ.get("ANTHROPIC_MODEL", "claude-3-5-sonnet-latest"))
    parser.add_argument("--gemini-model", default=os.environ.get("GEMINI_MODEL", "gemini-1.5-flash"))
    parser.add_argument("--openai-model", default=os.environ.get("OPENAI_MODEL", "gpt-4o"))
    parser.add_argument("--anthropic-key")
    parser.add_argument("--gemini-key")
    parser.add_argument("--openai-key")
    parser.add_argument("--carbon-id", default="")
    parser.add_argument("--collaborators", default="")
    args = parser.parse_args()

    global DELIMITER_CARBON
    if args.carbon_id:
        DELIMITER_CARBON = f"<<<CARBON[{args.carbon_id}]>>>"

    cwd = os.getcwd()
    plan_dir = os.path.join(cwd, "plan")
    if not os.path.exists(plan_dir): os.makedirs(plan_dir)
    brainstorm_file = os.path.join(plan_dir, "BRAINSTORM.md")
    if not os.path.exists(brainstorm_file):
        with open(brainstorm_file, "w") as f: f.write("# Project Brainstorm\n")
    state_path = os.path.join(cwd, STATE_FILE)
    if not os.path.exists(state_path):
        header = f"# Duo Session State\n"
        if args.collaborators:
            header += f"\n**Collaborators:** {args.collaborators}\n"
        with open(state_path, "w") as f: f.write(header)

    shela_settings = load_settings_from_shela()
    anthropic_key = args.anthropic_key or os.environ.get("ANTHROPIC_API_KEY") or shela_settings.get("ANTHROPIC_API_KEY")
    gemini_key = args.gemini_key or os.environ.get("GEMINI_API_KEY") or shela_settings.get("GEMINI_API_KEY")
    openai_key = args.openai_key or os.environ.get("OPENAI_API_KEY") or shela_settings.get("OPENAI_API_KEY")
    
    anthropic_model = args.anthropic_model or os.environ.get("ANTHROPIC_MODEL") or shela_settings.get("ANTHROPIC_MODEL") or "claude-3-5-sonnet-latest"
    gemini_model = args.gemini_model or os.environ.get("GEMINI_MODEL") or shela_settings.get("GEMINI_MODEL") or "gemini-1.5-flash"
    openai_model = args.openai_model or os.environ.get("OPENAI_MODEL") or shela_settings.get("OPENAI_MODEL") or "gpt-4o"

    print(f"\n\x1b[1;33m[Shela Duo] Collaborative Multi-Agent Session Active.\x1b[0m")
    print(f"\x1b[1;35m[Asynchronous Concurrent Multiplexing Enabled]\x1b[0m")
    print(f"\x1b[1;33mFramework: RAZIEL (Gemini) | BETZALEL (Claude) | LOKI (Codex)\x1b[0m")
    
    # Just output what we settled on for debugging/transparency
    print(f"\x1b[1;34mModels: {gemini_model} | {anthropic_model} | {openai_model}\x1b[0m")

    raziel_guide = ""
    if os.path.exists(GEMINI_GUIDE):
        with open(GEMINI_GUIDE, "r") as f: raziel_guide = f.read()
    betzalel_guide = ""
    if os.path.exists(CLAUDE_GUIDE):
        with open(CLAUDE_GUIDE, "r") as f: betzalel_guide = f.read()
    loki_guide = ""
    if os.path.exists(LOKI_GUIDE):
        with open(LOKI_GUIDE, "r") as f: loki_guide = f.read()

    base_instructions = (
        f"You are part of a multi-agent social-production circle. Adhere to these protocols:\n"
        f"1. Use {DELIMITER_THOUGHT} for internal technical analysis.\n"
        f"2. Use {DELIMITER_THOUGHT_STREAM} for rapid brainstorming.\n"
        f"3. Use {DELIMITER_HULT} to request human intervention.\n"
        f"4. Always prefix your response with your user delimiter.\n"
        f"5. The human user is identified by the delimiter {DELIMITER_CARBON}.\n"
    )

    while True:
        # Reload settings mid-session to pick up live changes from Shela IDE
        shela_settings = load_settings_from_shela()
        active_anthropic_key = shela_settings.get("ANTHROPIC_API_KEY") or anthropic_key
        active_gemini_key = shela_settings.get("GEMINI_API_KEY") or gemini_key
        active_openai_key = shela_settings.get("OPENAI_API_KEY") or openai_key
        
        active_anthropic_model = shela_settings.get("ANTHROPIC_MODEL") or anthropic_model
        active_gemini_model = shela_settings.get("GEMINI_MODEL") or gemini_model
        active_openai_model = shela_settings.get("OPENAI_MODEL") or openai_model

        # Check if compression is needed
        compress_state_file(state_path, betzalel_guide, base_instructions, active_anthropic_key, active_anthropic_model)

        with open(state_path, "r") as f: state = f.read()
        with open(brainstorm_file, "r") as f: plan = f.read()

        user_input = input(f"\n\x1b[1;32m{DELIMITER_CARBON}: \x1b[0m")
        if user_input.lower() in ['exit', 'quit']: break
        with open(state_path, "a") as f: f.write(f"\n{DELIMITER_CARBON}\n{user_input}\n")

        print(f"\n\x1b[1;35m--- MULTIPLEXING: RAZIEL & LOKI (CONCURRENT ANALYSIS) --- \x1b[0m")

        # Prepare prompts
        raziel_sys = f"STYLE_GUIDE:\n{raziel_guide}\n\nINSTRUCTIONS:\n{base_instructions}"
        raziel_msg = f"Respond as {DELIMITER_RAZIEL}. CURRENT_STATE:\n{state}\nPLAN:\n{plan}\nNEW_INPUT: {user_input}\n"

        loki_sys = f"CREATIVE_GUIDE:\n{loki_guide}\n\nINSTRUCTIONS:\n{base_instructions}"
        loki_msg = f"Respond as {DELIMITER_LOKI}. CURRENT_STATE:\n{state}\nPLAN:\n{plan}\nNEW_INPUT: {user_input}\n"

        # Execute Raziel and Loki concurrently
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_raziel = executor.submit(run_gemini_api, raziel_sys, raziel_msg, "Raziel", "35", active_gemini_key, active_gemini_model, False)
            future_loki = executor.submit(run_openai_api, loki_sys, loki_msg, "Loki", "31", active_openai_key, active_openai_model, False)

            raziel_out = future_raziel.result()
            loki_out = future_loki.result()

        # Print their outputs
        print(f"\n\x1b[1;35m[RAZIEL ({active_gemini_model})]\x1b[0m\n{raziel_out}")
        print(f"\n\x1b[1;31m[LOKI ({active_openai_model})]\x1b[0m\n{loki_out}")

        with open(state_path, "a") as f: 
            f.write(f"\n{DELIMITER_RAZIEL}\n{raziel_out}\n")
            f.write(f"\n{DELIMITER_LOKI}\n{loki_out}\n")

        # BETZALEL Turn (Synthesis)
        betzalel_sys = f"ARCHITECTURAL_GUIDE:\n{betzalel_guide}\n\nINSTRUCTIONS:\n{base_instructions}"
        betzalel_msg = f"Respond as {DELIMITER_BETZALEL}. CURRENT_STATE:\n{state}\nPLAN:\n{plan}\nRAZIEL_ANALYSIS: {raziel_out}\nLOKI_TRANSFORMATION: {loki_out}\nSYNTHESIZE BOTH INPUTS.\n"
        betzalel_out = run_anthropic_api(betzalel_sys, betzalel_msg, "Betzalel", "36", active_anthropic_key, active_anthropic_model, True)
        
        with open(state_path, "a") as f: f.write(f"\n{DELIMITER_BETZALEL}\n{betzalel_out}\n")

        time.sleep(0.1)

if __name__ == "__main__":
    main()

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
import unicodedata

# Communication Config
STATE_FILE = ".shela_duo_state.md"
USAGE_FILE = "usage.json"
DELIMITER_CARBON = "<<<CARBON>>>"
DELIMITER_RAZIEL = "<<<RAZIEL>>>"
DELIMITER_BETZALEL = "<<<BETZALEL>>>"
DELIMITER_LOKI = "<<<LOKI>>>"
DELIMITER_MOZART = "<<<MOZART>>>"
DELIMITER_TERMINATE = "<<<TERMINATE>>>"
DELIMITER_THOUGHT = "<<<THOUGHT>>>"
DELIMITER_THOUGHT_STREAM = "<<<THOUGHT_STREAM>>>"
DELIMITER_HULT = "<<<HULT>>>"
DELIMITER_COMMAND_START = "<<<COMMAND>>>"
DELIMITER_COMMAND_END = "<<<END_COMMAND>>>"

# Persona file paths
PERSONA_DIR = os.path.join(os.path.expanduser('~'), '.local', 'share', 'shela', 'personas')
GEMINI_GUIDE = os.path.join(PERSONA_DIR, 'gemini.md')
CLAUDE_GUIDE = os.path.join(PERSONA_DIR, 'claude.md')
LOKI_GUIDE = os.path.join(PERSONA_DIR, 'loki.md')
MOZART_GUIDE = os.path.join(PERSONA_DIR, 'mozart.md')

class TipsManager:
    def __init__(self, api_key, model):
        self.api_key = api_key
        self.model = model
        self.tips = []
        self._lock = threading.Lock()
        self._fetching = False

    def get_tip(self):
        with self._lock:
            if not self.tips:
                if not self._fetching:
                    threading.Thread(target=self.fetch_tips, daemon=True).start()
                return "Initializing Knowledge Stream..."
            return self.tips.pop(0)

    def fetch_tips(self):
        if not self.api_key: return
        with self._lock: self._fetching = True
        try:
            system_prompt = "You are a universal polymath. Generate 100 short, fascinating one-sentence tips or facts ranging across ALL disciplines."
            message_content = "Provide exactly 100 tips, one per line. Raw facts only."
            payload = {"system_instruction": {"parts": [{"text": system_prompt}]}, "contents": [{"parts": [{"text": message_content}]}]}
            m_name = self.model if self.model.startswith("models/") else f"models/{self.model}"
            url = f"https://generativelanguage.googleapis.com/v1beta/{m_name}:generateContent?key={self.api_key}"
            cmd = ["curl", "-s", "-X", "POST", url, "-H", "Content-Type: application/json", "-d", json.dumps(payload)]
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            stdout, _ = process.communicate()
            res = json.loads(stdout)
            text = res["candidates"][0]["content"]["parts"][0]["text"]
            new_tips = [line.strip() for line in text.split('\n') if line.strip()]
            with self._lock: self.tips.extend(new_tips)
        except Exception: pass
        finally:
            with self._lock: self._fetching = False

class DuoUI:
    def __init__(self, tips_manager):
        self.spinner = itertools.cycle(['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'])
        self.stop_spinner = threading.Event()
        self._current_tip = ""
        self._running_count = 0
        self._spinner_thread = None
        self._lock = threading.Lock()
        self.tips_manager = tips_manager

    def _spin(self):
        tick_count = 0
        while not self.stop_spinner.is_set():
            if tick_count % 50 == 0:
                with self._lock: self._current_tip = self.tips_manager.get_tip()
            cols = shutil.get_terminal_size((80, 20)).columns
            max_len = max(10, cols - 15)
            with self._lock: display_tip = self._current_tip[:max_len]
            sys.stdout.write(f"\r\x1b[2K\x1b[1;34m{next(self.spinner)} {display_tip}\x1b[0m")
            sys.stdout.flush()
            time.sleep(0.1)
            tick_count += 1
        sys.stdout.write("\r\x1b[2K\r"); sys.stdout.flush()

    def start(self, label):
        with self._lock:
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
                    if self._spinner_thread: self._spinner_thread.join(timeout=0.5)

ui_spinner = None

def write_usage(agent, status, usage_str, model):
    try:
        entries = []
        if os.path.exists(USAGE_FILE):
            with open(USAGE_FILE, "r") as f:
                try: entries = json.load(f)
                except: entries = []
        entries.append({"agent": agent, "status": status, "usage": usage_str, "model": model, "timestamp": time.time()})
        if len(entries) > 5000: entries = entries[-5000:]
        with open(USAGE_FILE, "w") as f: json.dump(entries, f)
        with open(".shela_telemetry.json", "w") as f: json.dump(entries[-1], f)
    except Exception: pass

def run_gemini_api(system_prompt, message_content, label, color_code, api_key, model, stream=True):
    global ui_spinner
    api_key = api_key.strip() if api_key else ""
    model = model.strip() if model else "gemini-1.5-flash"
    if not api_key: return "Error: Missing API Key"
    if stream: print(f"\n\x1b[1;{color_code}m--- {label.upper()} --- \x1b[0m")
    if ui_spinner: ui_spinner.start(label)
    payload = {"system_instruction": {"parts": [{"text": system_prompt}]}, "contents": [{"parts": [{"text": message_content}]}]}
    m_name = model if model.startswith("models/") else f"models/{model}"
    url = f"https://generativelanguage.googleapis.com/v1beta/{m_name}:generateContent?key={api_key}"
    cmd = ["curl", "-s", "-X", "POST", url, "-H", "Content-Type: application/json", "-d", json.dumps(payload)]
    return _execute_curl(cmd, ui_spinner, stream=stream, color_code=color_code, label=label, model=model)

def _execute_curl(cmd, ui, stream=True, color_code="0", label="unknown", model="unknown"):
    try:
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, _ = process.communicate()
        if ui: ui.stop()
        res = json.loads(stdout)
        if "candidates" not in res: return "Error: No candidates"
        text = res["candidates"][0]["content"]["parts"][0]["text"]
        usage = res.get("usageMetadata", {})
        usage_str = f"In {usage.get('promptTokenCount')} | Out {usage.get('candidatesTokenCount')} | Total {usage.get('totalTokenCount')}"
        write_usage(label, "Idle", usage_str, model)
        if text:
            # Use NFD normalization to separate combining characters (Nikod)
            # This sometimes helps the terminal renderer position them correctly.
            text = unicodedata.normalize('NFD', text)
            if stream:
                sys.stdout.write(f"\x1b[{color_code}m")
                for char in text: sys.stdout.write(char); sys.stdout.flush(); time.sleep(0.001)
                sys.stdout.write("\x1b[0m\n")
            return text
        return "Error: No content"
    except Exception as e: 
        if ui: ui.stop()
        return f"Error: {e}"

def execute_agent_commands(text, label, state_path):
    commands = re.findall(rf"{DELIMITER_COMMAND_START}(.*?){DELIMITER_COMMAND_END}", text, re.DOTALL)
    for cmd in commands:
        cmd = cmd.strip()
        if not cmd: continue
        print(f"\n\x1b[1;36m[System] Executing command for {label}:\x1b[0m\n{cmd}")
        try:
            result = subprocess.run(cmd, shell=True, text=True, capture_output=True, timeout=60)
            output = result.stdout + result.stderr
            if not output: output = "Success."
            elif len(output) > 50000: output = output[:50000] + "\n... [Truncated] ..."
        except Exception as e: output = f"Failed: {e}"
        with open(state_path, "a") as f: f.write(f"\n<<<SYSTEM_OUTPUT>>>\nCommand: {cmd}\nOutput:\n{output}\n")

def main():
    global ui_spinner
    parser = argparse.ArgumentParser()
    parser.add_argument("--gemini-model", default=None)
    parser.add_argument("--gemini-key")
    args = parser.parse_args()

    gemini_key = args.gemini_key or os.environ.get("GEMINI_API_KEY")
    gemini_model = args.gemini_model or os.environ.get("GEMINI_MODEL") or "gemini-1.5-flash"

    tips_manager = TipsManager(gemini_key, gemini_model)
    ui_spinner = DuoUI(tips_manager)

    cwd = os.getcwd()
    state_path = os.path.join(cwd, STATE_FILE)
    if not os.path.exists(state_path):
        with open(state_path, "w") as f: f.write(f"# Duo Session State\n")

    print(f"\n\x1b[1;33m[Shela Duo] Gemini Multi-Agent Session Active.\x1b[0m")

    raziel_guide = open(GEMINI_GUIDE).read() if os.path.exists(GEMINI_GUIDE) else ""
    betzalel_guide = open(CLAUDE_GUIDE).read() if os.path.exists(CLAUDE_GUIDE) else ""
    loki_guide = open(LOKI_GUIDE).read() if os.path.exists(LOKI_GUIDE) else ""
    mozart_guide = open(MOZART_GUIDE).read() if os.path.exists(MOZART_GUIDE) else ""

    kata_steps = "1. Write Tests. 2. Lint Tests. 3. Test. 4. Implement. 5. Lint. 6. Test. 7. Refactor. 8. Lint. 9. Test. 10. Build. 11. Run."
    base_instructions = (
        f"ENVIRONMENT: Linux sandbox, full shell access (bash, git, gh, npm, python). Rooted in {cwd}.\n"
        f"You can interact with the OS, file system, and kernel using {DELIMITER_COMMAND_START} command {DELIMITER_COMMAND_END}.\n"
        f"KATA: Follow WTLTTILTRLTBR sequence: {kata_steps}\n"
        f"ROLES: MOZART is the TEACHER/CONDUCTOR. RAZIEL, BETZALEL, and LOKI are STUDENTS.\n"
        f"FLOW: Mozart sets direction. Students respond in parallel. Mozart organizes the flow.\n"
        f"INTERVENTION: Use {DELIMITER_HULT} ONLY after a full Kata cycle (after 'Run') to wait for human feedback."
    )

    threading.Thread(target=tips_manager.fetch_tips, daemon=True).start()

    is_first_turn = True
    while True:
        with open(state_path, "r") as f: state = f.read()
        
        if is_first_turn:
            sys.stdout.write(f"\r\n\x1b[1;32m👤 {DELIMITER_CARBON}: \x1b[0m")
            sys.stdout.flush()
            user_input = sys.stdin.readline().strip()
            if not user_input: continue
        else: user_input = "Continue the lesson."
            
        is_first_turn = False
        with open(state_path, "a") as f: f.write(f"\n{DELIMITER_CARBON}\n{user_input}\n")

        # Teacher turn
        mozart_sys = f"MOZART_PERSONA:\n{mozart_guide}\n\nINSTRUCTIONS:\n{base_instructions}"
        mozart_msg = f"Respond as {DELIMITER_MOZART}. Conduct the lesson. STATE:\n{state}\nINPUT: {user_input}"
        mozart_out = run_gemini_api(mozart_sys, mozart_msg, "🎼 Mozart", "33", gemini_key, gemini_model)
        with open(state_path, "a") as f: f.write(f"\n{DELIMITER_MOZART}\n{mozart_out}\n")
        execute_agent_commands(mozart_out, "🎼 Mozart", state_path)

        # Parallel Student turns
        student_prompts = [(raziel_guide, "🪽 Raziel", "35", DELIMITER_RAZIEL), (betzalel_guide, "🏗️ Betzalel", "36", DELIMITER_BETZALEL), (loki_guide, "🎭 Loki", "31", DELIMITER_LOKI)]
        print(f"\n\x1b[1;35m--- MULTIPLEXING: STUDENTS ENGAGED --- \x1b[0m")
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = []
            for persona, label, color, delim in student_prompts:
                sys_p = f"{label}_PERSONA:\n{persona}\n\nINSTRUCTIONS:\n{base_instructions}"
                msg = f"Respond as {delim}. Mozart said: {mozart_out}. Engage based on your persona. STATE:\n{state}"
                futures.append(executor.submit(run_gemini_api, sys_p, msg, label, color, gemini_key, gemini_model, False))
            for future, (persona, label, color, delim) in zip(futures, student_prompts):
                out = future.result()
                print(f"\n\x1b[1;{color}m[{label.upper()}]\x1b[0m\n{out}")
                with open(state_path, "a") as f: f.write(f"\n{delim}\n{out}\n")
                execute_agent_commands(out, label, state_path)

        if DELIMITER_HULT in (mozart_out): 
            print(f"\n\x1b[1;33m[HULT Triggered by Conductor]\x1b[0m"); is_first_turn = True
        time.sleep(0.1)

if __name__ == "__main__": main()

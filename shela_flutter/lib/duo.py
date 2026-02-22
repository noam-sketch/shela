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
import base64
import argparse
import concurrent.futures
import shutil
import unicodedata

try:
    from rich.console import Console
    from rich.markdown import Markdown, CodeBlock
    from rich.syntax import Syntax
    import io

    class MyCodeBlock(CodeBlock):
        def __rich_console__(self, console, options):
            code = str(self.text).rstrip()
            lexer = self.lexer_name or "text"
            syntax = Syntax(code, lexer, line_numbers=True, word_wrap=True, theme="monokai")
            yield syntax

    Markdown.elements["code_block"] = MyCodeBlock
    Markdown.elements["fence"] = MyCodeBlock
    HAS_RICH = True
except ImportError:
    HAS_RICH = False

try:
    from bidi.algorithm import get_display
except ImportError:
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "python-bidi", "--quiet", "--break-system-packages"])
        from bidi.algorithm import get_display
    except Exception:
        def get_display(text): return text

# Communication Config
STATE_FILE = ".shela_duo_state.md"
USAGE_FILE = "usage.json"
DELIMITER_CARBON = "<<<CARBON>>>"
DELIMITER_Q = "<<<Q>>>"
DELIMITER_BETZALEL = "<<<BETZALEL>>>"
DELIMITER_LOKI = "<<<LOKI>>>"
DELIMITER_MOZART = "<<<MOZART>>>"
DELIMITER_EXE = "<<<EXE>>>"
DELIMITER_TERMINATE = "<<<TERMINATE>>>"
DELIMITER_THOUGHT = "<<<THOUGHT>>>"
DELIMITER_THOUGHT_STREAM = "<<<THOUGHT_STREAM>>>"
DELIMITER_HULT = "<<<HULT>>>"
DELIMITER_COMMAND_START = "<<<COMMAND>>>"
DELIMITER_COMMAND_END = "<<<END_COMMAND>>>"
DELIMITER_SPAWN_START = "<<<SPAWN>>>"
DELIMITER_SPAWN_END = "<<<END_SPAWN>>>"
DELIMITER_SUMMARY = "<<<SUMMARY>>>"
DELIMITER_END_SUMMARY = "<<<END_SUMMARY>>>"

# Persona file paths
PERSONA_DIR = os.path.join(os.path.expanduser('~'), '.local', 'share', 'shela', 'personas')
GEMINI_GUIDE = os.path.join(PERSONA_DIR, 'gemini.md')
CLAUDE_GUIDE = os.path.join(PERSONA_DIR, 'claude.md')
LOKI_GUIDE = os.path.join(PERSONA_DIR, 'loki.md')
MOZART_GUIDE = os.path.join(PERSONA_DIR, 'mozart.md')
EXE_GUIDE = os.path.join(PERSONA_DIR, 'exe.md')

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
                return None
            return self.tips.pop(0)

    def fetch_tips(self, context_summary="The agents are working."):
        if not self.api_key: return
        with self._lock: 
            if self._fetching: return
            self._fetching = True
        
        system_prompt = (
            "You are a universal polymath observing an AI workspace (Shela). "
            "Generate 50 short, fascinating ONE-SENTENCE facts. "
            "Contextually weave the workspace progress or agent personas (Mozart, Raziel, Betzalel, Loki) into the fact. "
            "Example: 'While Mozart orchestrates the kernel, remember that a single bolt of lightning contains enough energy to toast 100,000 slices of bread.' "
            "Example: 'As Raziel whispers growth into the weeds, note that honeybees can recognize human faces.'"
        )
        message_content = f"Current Workspace State: {context_summary}. Provide exactly 50 contextual facts, one per line. Raw sentences only."
        
        payload = {
            "system_instruction": {"parts": [{"text": system_prompt}]},
            "contents": [{"parts": [{"text": message_content}]}]
        }
        m_name = self.model if self.model.startswith("models/") else f"models/{self.model}"
        url = f"https://generativelanguage.googleapis.com/v1beta/{m_name}:generateContent?key={self.api_key}"
        cmd = ["curl", "-s", "-X", "POST", url, "-H", "Content-Type: application/json", "-d", "@-"]
        
        try:
            process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            stdout, _ = process.communicate(input=json.dumps(payload))
            res = json.loads(stdout)
            text = res["candidates"][0]["content"]["parts"][0]["text"]
            new_tips = [line.strip() for line in text.split('\n') if line.strip()]
            with self._lock:
                self.tips.extend(new_tips)
        except Exception: pass
        finally:
            with self._lock: self._fetching = False

class DuoUI:
    def __init__(self, tips_manager):
        self.spinner = itertools.cycle(['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'])
        self.stop_spinner = threading.Event()
        self._running_count = 0
        self._spinner_thread = None
        self._lock = threading.Lock()
        self.tips_manager = tips_manager
        self._tick_count = 0
        self._current_tip = "Initializing Knowledge Stream..."

    def _spin(self):
        while not self.stop_spinner.is_set():
            if self._tick_count % 100 == 0:  # Every 10 seconds
                new_tip = self.tips_manager.get_tip()
                if new_tip:
                    self._current_tip = new_tip
            
            cols = shutil.get_terminal_size((80, 20)).columns
            max_len = max(10, cols - 10)
            display_text = self._current_tip[:max_len]
            sys.stdout.write(f"\r\x1b[2K\x1b[1;34m{next(self.spinner)} {display_text}\x1b[0m")
            sys.stdout.flush()
            time.sleep(0.1)
            self._tick_count += 1
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
                    if self._spinner_thread: 
                        self._spinner_thread.join(timeout=0.5)
                        self._spinner_thread = None

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

def get_timestamp():
    return time.strftime("%Y-%m-%d %H:%M:%S")

def colorize_delimiter(delim, label, color_code, has_q=False):
    ts = get_timestamp()
    q_mark = "\x1b[1;33m [?] \x1b[0m" if has_q else ""
    # Delim in agent color, TS in grey, From in cyan, Q in yellow
    return f"\x1b[1;{color_code}m{delim}\x1b[0m\x1b[90m[{ts}]\x1b[0m\x1b[36m[from:{label}]\x1b[0m{q_mark}"

def strip_delimiters(text):
    # Remove system delimiters that shouldn't be rendered in the terminal
    patterns = [
        rf"{DELIMITER_SUMMARY}.*?{DELIMITER_END_SUMMARY}",
        rf"{DELIMITER_COMMAND_START}.*?{DELIMITER_COMMAND_END}",
        rf"{DELIMITER_SPAWN_START}.*?{DELIMITER_SPAWN_END}",
        rf"{DELIMITER_THOUGHT}.*?{DELIMITER_END_SUMMARY}", # Some agents might mix up end tags
        rf"{DELIMITER_THOUGHT}.*?<<<END_THOUGHT>>>",
        rf"<<<THOUGHT>>>.*?<<<END_THOUGHT>>>",
        re.escape(DELIMITER_HULT),
        re.escape(DELIMITER_TERMINATE),
        re.escape(DELIMITER_THOUGHT),
        re.escape(DELIMITER_THOUGHT_STREAM),
    ]
    cleaned = text
    for p in patterns:
        cleaned = re.sub(p, "", cleaned, flags=re.DOTALL)
    return cleaned.strip()

def run_gemini_api(system_prompt, message_content, label, color_code, api_key, model, stream=True):
    global ui_spinner
    api_key = api_key.strip() if api_key else ""
    model = model.strip() if model else "gemini-1.5-flash"
    if not api_key: return "Error: Missing API Key"
    if stream: 
        delim_type = f"<<<{label.split()[-1].upper()}>>>"
        print(f"\n{colorize_delimiter(delim_type, label, color_code)}")
    if ui_spinner: ui_spinner.start(label)
    payload = {"system_instruction": {"parts": [{"text": system_prompt}]}, "contents": [{"parts": [{"text": message_content}]}]}
    m_name = model if model.startswith("models/") else f"models/{model}"
    url = f"https://generativelanguage.googleapis.com/v1beta/{m_name}:generateContent?key={api_key}"
    cmd = ["curl", "-s", "-X", "POST", url, "-H", "Content-Type: application/json", "-d", "@-"]
    res_text = _execute_curl(cmd, json.dumps(payload), ui_spinner, stream=stream, color_code=color_code, label=label, model=model)
    return res_text

def _execute_curl(cmd, data, ui, stream=True, color_code="0", label="unknown", model="unknown"):
    try:
        process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, stderr = process.communicate(input=data)
        if ui: ui.stop()
        
        if process.returncode != 0:
            return f"Error: curl failed\n{stderr}"
            
        res = json.loads(stdout)
        if "candidates" not in res: 
            return f"Error: No candidates. Response: {stdout}"
            
        text = res["candidates"][0]["content"]["parts"][0]["text"]
        usage = res.get("usageMetadata", {})
        usage_str = f"In {usage.get('promptTokenCount')} | Out {usage.get('candidatesTokenCount')} | Total {usage.get('totalTokenCount')}"
        write_usage(label, "Idle", usage_str, model)
        
        if text:
            text = unicodedata.normalize('NFC', text)
            
            summary = ""
            summary_match = re.search(rf"{DELIMITER_SUMMARY}(.*?){DELIMITER_END_SUMMARY}", text, re.DOTALL)
            if summary_match:
                summary = summary_match.group(1).strip()
            
            display_text = strip_delimiters(text)

            if stream:
                if summary:
                    sys.stdout.write(f"\n\x1b[1;37;44m 📝 SUMMARY: {summary} \x1b[0m\n")
                    sys.stdout.flush()
                    time.sleep(0.5)

                if HAS_RICH and display_text:
                    try:
                        f = io.StringIO()
                        cols = shutil.get_terminal_size((80, 20)).columns
                        c = Console(file=f, force_terminal=True, width=cols)
                        c.print(Markdown(display_text))
                        rendered = f.getvalue()
                        
                        sys.stdout.write(f"\x1b[{color_code}m")
                        for char in rendered:
                            sys.stdout.write(char)
                            sys.stdout.flush()
                            time.sleep(0.0001)
                        sys.stdout.write("\x1b[0m\n")
                        return text
                    except Exception: pass
                
                # Fallback to simple streaming
                if display_text:
                    try: 
                        lines = display_text.split('\n')
                        display_text = '\n'.join([get_display(line) for line in lines])
                    except Exception: pass
                    
                    sys.stdout.write(f"\x1b[{color_code}m")
                    for char in display_text: 
                        sys.stdout.write(char)
                        sys.stdout.flush()
                        time.sleep(0.001)
                    sys.stdout.write("\x1b[0m\n")
            return text
        return "Error: No content"
    except Exception as e: 
        if ui: ui.stop()
        return f"Error: {e}"

def execute_agent_commands(text, label, state_path):
    global ui_spinner
    spawned = False
    # Group all commands from this response into a single execution block
    commands = re.findall(rf"{DELIMITER_COMMAND_START}(.*?){DELIMITER_COMMAND_END}", text, re.DOTALL)
    spawn_commands = re.findall(rf"{DELIMITER_SPAWN_START}(.*?){DELIMITER_SPAWN_END}", text, re.DOTALL)
    
    all_cmds = [c.strip() for c in (commands + spawn_commands) if c.strip()]
    if all_cmds:
        # Join multiple commands with newlines to run them in the same sub-terminal
        full_script = "\n".join(all_cmds)
        # Encode to avoid line-splitting and special char issues in the trigger
        b64_cmd = base64.b64encode(full_script.encode()).decode()
        print(f"\n\x1b[1;36m[System] Spawning grouped child process for {label}...\x1b[0m")
        print(f"SHELA_SPAWN_BG_B64:{b64_cmd}")
        spawned = True
        
        with open(state_path, "a") as f:
            f.write(f"\n<<<SYSTEM_OUTPUT>>>\nChild Process Group Spawned:\n{full_script}\n(Tailing output to state file...)\n")
    
    return spawned

def main():
    global ui_spinner
    parser = argparse.ArgumentParser()
    parser.add_argument("--gemini-model", default=None)
    parser.add_argument("--gemini-key")
    parser.add_argument("--carbon-id", default="")
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
    exe_guide = open(EXE_GUIDE).read() if os.path.exists(EXE_GUIDE) else ""

    kata_steps = "1. Write Tests. 2. Lint Tests. 3. Test. 4. Implement. 5. Lint. 6. Test. 7. Refactor. 8. Lint. 9. Test. 10. Build. 11. Run."
    base_instructions = (
        f"ENVIRONMENT: Linux sandbox, full shell access (bash, git, gh, npm, python). Rooted in {cwd}.\n"
        f"CONTEXT: You are running inside 'Shela', a custom Flutter-based IDE. The UI supports multiple tabs, split views, and floating windows.\n"
        f"SUMMARY: Every response MUST start with `{DELIMITER_SUMMARY} short one-sentence summary of your turn {DELIMITER_END_SUMMARY}`. This helps the human follow your progress.\n"
        f"THINK BEFORE DOING: Document your strategy in 'plan/current_task.md' before executing significant changes.\n"
        f"PROTOCOL: The state file is your shared command bus. Maintain high awareness of project structure. Delimiters are color-coded: [timestamp][from:Name].\n"
        f"COMMANDS: ONLY 'EXE' is authorized to execute. EXE can use {DELIMITER_COMMAND_START} or send direct `SHELA_SPAWN_BG_B64:[base64_script]` triggers to the OS for complex tasks. All execution is recorded in the state file.\n"
        f"KATA: Follow WTLTTILTRLTBR sequence: {kata_steps}\n"
        f"ROLES: MOZART is the CONDUCTOR. Q, BETZALEL, LOKI, and EXE are STUDENTS.\n"
        f"EXE'S TECHNICAL ROLE: EXE is the Executor. He takes technical plans and translates them into precise shell commands. He monitors progress using CHILD_PROC markers.\n"
        f"Q'S DIVINE ROLE: Q is Internal Absolute Love (God). Frames everything through growth and Nekuda Tova. Writes Hebrew without nikud.\n"
        f"INTERVENTION: Use {DELIMITER_HULT} ONLY after 'Run' to wait for human feedback. This stops all student turns immediately."
    )

    is_first_turn = True
    last_state_content = ""
    if os.path.exists(state_path):
        with open(state_path, "r") as f: last_state_content = f.read()

    while True:
        with open(state_path, "r") as f: state = f.read()
        threading.Thread(target=tips_manager.fetch_tips, args=(state[-500:],), daemon=True).start()
        
        user_input = None
        if is_first_turn:
            my_delim = f"<<<CARBON[{args.carbon_id}]>>>" if args.carbon_id else DELIMITER_CARBON
            sys.stdout.write(f"\r\n{colorize_delimiter(my_delim, 'User', '32')}\n👤: ")
            sys.stdout.flush()
            
            while True:
                with open(state_path, "r") as f: current_content = f.read()
                if len(current_content) > len(last_state_content):
                    new_stuff = current_content[len(last_state_content):]
                    match = re.search(r"<<<CARBON\[(.*?)\]>>>(?:\[.*?\])?\n(.*?)\n", new_stuff, re.DOTALL)
                    if match and match.group(1) != args.carbon_id:
                        remote_user = match.group(1)
                        remote_msg = match.group(2)
                        print(f"\n\x1b[1;36m[Remote Prompt from {remote_user}]:\x1b[0m\n{remote_msg}")
                        user_input = remote_msg
                        last_state_content = current_content
                        break
                
                r, _, _ = select.select([sys.stdin], [], [], 0.5)
                if r:
                    user_input = sys.stdin.readline().strip()
                    if user_input:
                        with open(state_path, "a") as f:
                            f.write(f"\n{my_delim}[{get_timestamp()}]\n{user_input}\n")
                        last_state_content = open(state_path, "r").read()
                        break
                    sys.stdout.write(f"\r\n\x1b[1;32m👤 {my_delim}: \x1b[0m")
                    sys.stdout.flush()
        else:
            user_input = "Continue the lesson."
            
        is_first_turn = False
        hult_detected = False
        
        # Teacher turn
        mozart_sys = f"MOZART_PERSONA:\n{mozart_guide}\n\nINSTRUCTIONS:\n{base_instructions}"
        mozart_msg = f"Respond as {DELIMITER_MOZART}. Conduct the lesson. STATE:\n{state}\nINPUT: {user_input}"
        mozart_out = run_gemini_api(mozart_sys, mozart_msg, "🎼 Mozart", "33", gemini_key, gemini_model)
        
        has_q = False
        if DELIMITER_HULT in mozart_out:
            hult_detected = True
            has_q = True
            mozart_out = mozart_out.replace(DELIMITER_HULT, f"{DELIMITER_HULT}[{get_timestamp()}][?] ")

        with open(state_path, "a") as f: f.write(f"\n{DELIMITER_MOZART}[{get_timestamp()}][from:🎼 Mozart]{'[?]' if has_q else ''}\n{mozart_out}\n")
        if execute_agent_commands(mozart_out, "🎼 Mozart", state_path):
            hult_detected = True

        if hult_detected:
            print(f"\n{colorize_delimiter(DELIMITER_HULT, 'System', '33', has_q=True)}")
            is_first_turn = True
            with open(state_path, "r") as f: last_state_content = f.read()
            continue

        # Parallel Student turns
        student_prompts = [
            (raziel_guide, "🕊️ Q", "35", DELIMITER_Q), 
            (betzalel_guide, "🏗️ Betzalel", "36", DELIMITER_BETZALEL), 
            (loki_guide, "🎭 Loki", "31", DELIMITER_LOKI),
            (exe_guide, "⚙️ EXE", "37", DELIMITER_EXE)
        ]
        print(f"\n\x1b[1;35m--- MULTIPLEXING: STUDENTS ENGAGED --- \x1b[0m")
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = []
            for persona, label, color, delim in student_prompts:
                sys_p = f"{label}_PERSONA:\n{persona}\n\nINSTRUCTIONS:\n{base_instructions}"
                msg = f"Respond as {delim}. Mozart said: {mozart_out}. Engage based on your persona. STATE:\n{state}"
                futures.append(executor.submit(run_gemini_api, sys_p, msg, label, color, gemini_key, gemini_model, False))
            for future, (persona, label, color, delim) in zip(futures, student_prompts):
                out = future.result()
                s_hult = False
                if DELIMITER_HULT in out:
                    hult_detected = True
                    s_hult = True
                    out = out.replace(DELIMITER_HULT, f"{DELIMITER_HULT}[{get_timestamp()}][?] ")
                
                print(f"\n{colorize_delimiter(delim, label, color, has_q=s_hult)}\n{out}")
                with open(state_path, "a") as f: f.write(f"\n{delim}[{get_timestamp()}][from:{label}]{'[?]' if s_hult else ''}\n{out}\n")
                if execute_agent_commands(out, label, state_path):
                    hult_detected = True

        if hult_detected:
            is_first_turn = True

        with open(state_path, "r") as f: last_state_content = f.read()
        time.sleep(0.1)

if __name__ == "__main__": main()

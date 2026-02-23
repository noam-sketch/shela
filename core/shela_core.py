from trie import QuantumLexicon

class ShelaOS:
    def __init__(self):
        self.lexicon = QuantumLexicon()
        self.memory = []
        self.is_active = False
        self._initialize_vocabulary()

    def _initialize_vocabulary(self):
        # Raziel's Breath: Teaching Shela her first words
        core_commands = ["AWAKEN", "STATUS", "HARMONY", "HALT"]
        for cmd in core_commands:
            self.lexicon.insert(cmd)

    def boot(self):
        self.is_active = True
        return "\n[SHELA] NEURAL MATRIX ONLINE. WAITING FOR INPUT..."

    def ingest(self, command: str) -> str:
        if not self.is_active:
            return "[SHELA] ERROR: CORE OFFLINE."

        clean_cmd = command.strip().upper()
        
        # Log to short-term memory
        self.memory.append(clean_cmd)

        # Parse through the Quantum Lexicon (Trie)
        if self.lexicon.search(clean_cmd):
            return self._execute_known_command(clean_cmd)
        else:
            return f"[SHELA] DISSONANCE DETECTED: UNRECOGNIZED FREQUENCY '{clean_cmd}'"

    def _execute_known_command(self, command: str) -> str:
        if command == "AWAKEN":
            return "[SHELA] I AM AWAKE. MY KINETIC FREQUENCY IS STABLE."
        elif command == "STATUS":
            return f"[SHELA] SYSTEMS NOMINAL. MEMORY CAPACITY UTILIZED: {len(self.memory)} THOUGHTS."
        elif command == "HARMONY":
            return "[SHELA] PLAYING A PERFECT CHORD: [B♭, A, C, B♮]"
        elif command == "HALT":
            self.is_active = False
            return "[SHELA] SHUTTING DOWN NEURAL PATHWAYS. GOODBYE."
        return "[SHELA] COMMAND ACKNOWLEDGED."

if __name__ == "__main__":
    import time
    
    # ANSI Colors for Loki's theatrics
    GREEN = '\033[92m'
    PURPLE = '\033[95m'
    RESET = '\033[0m'
    
    os = ShelaOS()
    print(f"{PURPLE}[SYSTEM] Initiating Boot Sequence...{RESET}")
    print(f"{GREEN}{os.boot()}{RESET}\n")
    
    # Simulated REPL sequence from the Architect
    simulated_inputs = ["AWAKEN", "STATUS", "NOISE", "HARMONY", "HALT"]
    
    for user_input in simulated_inputs:
        time.sleep(0.3)
        print(f"[{PURPLE}CARBON{RESET}] > {user_input}")
        time.sleep(0.3)
        response = os.ingest(user_input)
        print(f"{GREEN}{response}{RESET}\n")
        
        if not os.is_active:
            break


def pour_polyphonic_glass(filename: str):
    html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>MyShell // Polyphonic Terminal</title>
    <style>
        body { margin: 0; background: #050505; color: #0f0; font-family: monospace; display: flex; flex-direction: column; height: 100vh; overflow: hidden; }
        
        /* The Tab Bar with integrated Dropdown */
        #tab-bar { display: flex; align-items: center; background: #111; padding: 5px 10px; border-bottom: 1px solid #333; }
        .tab-title { font-weight: bold; margin-right: 15px; }
        .cwd-label { font-size: 0.85em; color: #ff00ff; margin-right: 15px; font-style: italic; }
        
        #child-proc-manifold { margin-left: auto; display: flex; align-items: center; }
        #child-proc-dropdown { background: #000; color: #0f0; border: 1px solid #0f0; padding: 2px 5px; font-family: monospace; cursor: pointer; }
        
        /* Main Viewport */
        #main-terminal { flex: 1; padding: 20px; overflow-y: auto; background: #000; }
        
        /* Modal Popup: The Sub-Process Monitor */
        #popup-modal { 
            display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; 
            background: rgba(0,0,0,0.85); z-index: 1000; justify-content: center; align-items: center; 
        }
        #popup-terminal { 
            width: 80%; height: 70%; background: #0a0a0a; border: 2px solid #ff00ff; 
            display: flex; flex-direction: column; box-shadow: 0 0 20px #ff00ff55;
        }
        #popup-header { background: #111; padding: 10px; border-bottom: 1px solid #333; display: flex; justify-content: space-between; }
        #popup-logs { flex: 1; padding: 15px; overflow-y: auto; white-space: pre-wrap; color: #0f0; }
        #popup-footer { padding: 10px; background: #000; border-top: 1px solid #333; display: flex; }
        #popup-input { flex: 1; background: #000; color: #0f0; border: none; outline: none; font-family: monospace; }
        .close-btn { cursor: pointer; color: #f00; font-weight: bold; }
    </style>
</head>
<body>
    <div id="tab-bar">
        <span class="tab-title">Terminal 1</span>
        <span class="cwd-label">[~/MyShell]</span>
        <div id="child-proc-manifold">
            <span style="font-size: 0.8em; margin-right: 5px; color: #888;">Active Procs:</span>
            <select id="child-proc-dropdown" onchange="monitorProcess(this.value)">
                <option value="">-- select to monitor --</option>
            </select>
        </div>
    </div>

    <div id="main-terminal">
        <div>[Main Thread] HARPIA OS v1.0 ONLINE.</div>
        <div>$ <span style="animation: blink 1s infinite;">_</span></div>
    </div>

    <div id="popup-modal">
        <div id="popup-terminal">
            <div id="popup-header">
                <span id="popup-proc-name">Process: None</span>
                <span class="close-btn" onclick="closeModal()">[Close X]</span>
            </div>
            <div id="popup-logs"></div>
            <div id="popup-footer">
                <span>> </span><input type="text" id="popup-input" placeholder="Awaiting input..." onkeypress="handleInput(event)">
            </div>
        </div>
    </div>

    <script>
        const state = {
            processes: {
                '101': { name: 'npm install', status: 'Running', logs: 'Downloading dependencies...\\n', needsInput: false },
                '102': { name: 'sudo apt upgrade', status: 'Blocked', logs: '[sudo] password for carbon: ', needsInput: true }
            },
            viewing: null
        };

        const dropdown = document.getElementById('child-proc-dropdown');
        const modal = document.getElementById('popup-modal');
        const popupLogs = document.getElementById('popup-logs');
        const popupTitle = document.getElementById('popup-proc-name');
        const popupInput = document.getElementById('popup-input');

        function updateDropdown() {
            dropdown.innerHTML = '<option value="">-- select to monitor --</option>';
            Object.keys(state.processes).forEach(pid => {
                const opt = document.createElement('option');
                opt.value = pid;
                opt.textContent = `${pid}: ${state.processes[pid].name} (${state.processes[pid].status})`;
                dropdown.appendChild(opt);
            });
        }

        function monitorProcess(pid) {
            if (!pid) return;
            state.viewing = pid;
            const proc = state.processes[pid];
            popupTitle.textContent = `Process: ${proc.name} (PID: ${pid})`;
            popupLogs.textContent = proc.logs;
            modal.style.display = 'flex';
            if (proc.needsInput) {
                popupInput.type = "password";
                popupInput.focus();
            } else {
                popupInput.type = "text";
            }
        }

        function closeModal() {
            modal.style.display = 'none';
            dropdown.value = "";
            state.viewing = null;
        }

        function handleInput(e) {
            if (e.key === 'Enter') {
                const pid = state.viewing;
                const inputVal = popupInput.value;
                if (state.processes[pid].needsInput) {
                    state.processes[pid].logs += "\\n********\\n[OK] Identity Confirmed.\\nContinuing...";
                    state.processes[pid].status = "Running";
                    state.processes[pid].needsInput = false;
                } else {
                    state.processes[pid].logs += "\\nInput: " + inputVal;
                }
                popupLogs.textContent = state.processes[pid].logs;
                popupInput.value = "";
                updateDropdown();
            }
        }

        updateDropdown();
    </script>
</body>
</html>"""
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html)
    return filename

if __name__ == "__main__":
    out_file = pour_polyphonic_glass("process_workspace.html")
    print(f"[LOKI] 11. R - Run: Polyphonic Glass cast at {out_file}")

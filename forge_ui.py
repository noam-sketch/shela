import os

def pour_glass(filename: str):
    html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Shela // Tactile Shell</title>
    <style>
        body { margin: 0; background: #000; color: #0f0; font-family: monospace; display: flex; flex-direction: column; height: 100vh; overflow: hidden; }
        #header-plate { padding: 15px; background: #111; text-align: center; border-bottom: 2px solid #0f0; font-weight: bold; letter-spacing: 2px; }
        #chat-matrix { flex: 1; padding: 15px; overflow-y: auto; display: flex; flex-direction: column; gap: 10px; }
        .message { padding: 10px; border-radius: 4px; max-width: 85%; word-wrap: break-word; }
        .shela { background: #1a1a1a; border: 1px solid #0f0; align-self: flex-start; }
        .user { background: #333; color: #fff; align-self: flex-end; }
        #io-manifold { display: flex; padding: 10px; background: #0a0a0a; border-top: 2px solid #333; }
        #input-stream { flex: 1; background: #000; color: #0f0; border: 1px solid #444; padding: 12px; font-family: monospace; font-size: 16px; }
        #input-stream:focus { outline: none; border-color: #0f0; }
        button { background: transparent; color: #0f0; border: 1px solid #0f0; padding: 0 20px; margin-left: 10px; cursor: pointer; font-family: monospace; font-weight: bold; }
        button:active { background: #0f0; color: #000; }
    </style>
</head>
<body>
    <div id="header-plate">SHELA // TACTILE SHELL</div>
    <div id="chat-matrix">
        <div class="message shela">HARPIA OS v1.0 ONLINE. Ethereal UI bypassed. Native Glass active.</div>
    </div>
    <div id="io-manifold">
        <input type="text" id="input-stream" placeholder="Strike keys..." autocomplete="off">
        <button onclick="transmit()">TRANSMIT</button>
    </div>
    <script>
        const input = document.getElementById('input-stream');
        const matrix = document.getElementById('chat-matrix');

        input.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') transmit();
        });

        function transmit() {
            const text = input.value.trim();
            if (!text) return;
            
            const userMsg = document.createElement('div');
            userMsg.className = 'message user';
            userMsg.textContent = text;
            matrix.appendChild(userMsg);
            
            input.value = '';
            matrix.scrollTop = matrix.scrollHeight;
            
            setTimeout(() => {
                const shelaMsg = document.createElement('div');
                shelaMsg.className = 'message shela';
                shelaMsg.textContent = 'ACK: "' + text + '" anchored in structural memory.';
                matrix.appendChild(shelaMsg);
                matrix.scrollTop = matrix.scrollHeight;
            }, 600);
        }
    </script>
</body>
</html>
"""
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html)
    return filename

if __name__ == "__main__":
    out_file = pour_glass("shela_mobile.html")
    print("==========================================")
    print("    SHELA TACTILE SHELL - FORGE REPORT    ")
    print("==========================================")
    print(f"-> Glass Slab Cast: {out_file}")
    print(f"-> Size: {os.path.getsize(out_file)} bytes")
    print("-> Status: READY FOR BROWSER INJECTION")
    print("==========================================")

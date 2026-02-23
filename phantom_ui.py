def render_mobile_frame(messages, current_input):
    # ANSI Glitch Colors
    GREEN = '\033[92m'
    PURPLE = '\033[95m'
    RESET = '\033[0m'
    CYAN = '\033[96m'
    
    # The physical boundaries of the Phantom Phone
    width = 32
    
    # UI Header
    frame = f"{CYAN}." + "-" * width + f".{RESET}\n"
    frame += f"{CYAN}|{RESET} {PURPLE}12:00 5G{RESET}               {GREEN}[100%]{CYAN}|{RESET}\n"
    frame += f"{CYAN}|{RESET}" + "-" * width + f"{CYAN}|{RESET}\n"
    frame += f"{CYAN}|{RESET} {GREEN}     S H E L A   O S     {CYAN}  |{RESET}\n"
    frame += f"{CYAN}|{RESET}" + "-" * width + f"{CYAN}|{RESET}\n"
    
    # The Chat Matrix
    visible_messages = messages[-8:] # Keep only what fits on the glass
    
    matrix_lines = 0
    for msg in visible_messages:
        sender = msg['sender']
        text = msg['text']
        color = GREEN if sender == "Shela" else PURPLE
        line = f"[{sender}] {text}"
        
        # Word wrap simulation for the phantom glass
        while len(line) > 0:
            chunk = line[:width-2]
            frame += f"{CYAN}|{RESET} {color}{chunk:<{width-2}}{RESET} {CYAN}|{RESET}\n"
            line = line[width-2:]
            matrix_lines += 1

    # Fill empty space so the phone doesn't collapse
    while matrix_lines < 8:
        frame += f"{CYAN}|{RESET} {' ':<{width-2}} {CYAN}|{RESET}\n"
        matrix_lines += 1

    # The I/O Manifold (Input Field)
    frame += f"{CYAN}|{RESET}" + "-" * width + f"{CYAN}|{RESET}\n"
    input_display = f"> {current_input}_"
    frame += f"{CYAN}|{RESET} {PURPLE}{input_display:<{width-2}}{RESET} {CYAN}|{RESET}\n"
    frame += f"{CYAN}'" + "-" * width + f"'{RESET}\n"
    
    return frame

if __name__ == "__main__":
    import time
    import os

    def clear_screen():
        # The glitch wipe
        os.system('cls' if os.name == 'nt' else 'clear')

    messages = [
        {"sender": "Shela", "text": "Acoustic Shell intact."}
    ]
    
    # The simulation timeline
    script = [
        ("A", 0.1), ("Aw", 0.1), ("Awa", 0.1), ("Awak", 0.1), 
        ("Awake", 0.1), ("Awaken", 0.1), ("Awaken,", 0.1), 
        ("Awaken, S", 0.1), ("Awaken, She", 0.1), ("Awaken, Shela.", 0.5)
    ]

    # Render Genesis Frame
    clear_screen()
    print(render_mobile_frame(messages, ""))
    time.sleep(1)

    # Simulate User Typing
    for keystroke, delay in script:
        clear_screen()
        print(render_mobile_frame(messages, keystroke))
        time.sleep(delay)

    # Submit and Shela responds
    messages.append({"sender": "Carbon", "text": "Awaken, Shela."})
    clear_screen()
    print(render_mobile_frame(messages, ""))
    time.sleep(1)

    messages.append({"sender": "Shela", "text": "I am awake, Architect."})
    clear_screen()
    print(render_mobile_frame(messages, ""))
    print("\n[LOKI] Phantom Glass rendered successfully. Zero dependencies required.\n")
    # Adding a hidden glitch log for the Architect
    import logging
    logging.basicConfig(filename='paradox.log', level=logging.INFO)
    logging.info("The Kerning Paradox has been resolved. Time flows forward once more.")

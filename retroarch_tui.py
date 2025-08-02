#!/usr/bin/env python3
import curses
import json
import os
import subprocess
import traceback

VALID_EXTS = ('.zip', '.nes', '.sfc', '.smc', '.gba', '.gb', '.gbc')

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(SCRIPT_DIR, "config.json")

with open(CONFIG_PATH, "r") as f:
    CONFIG = json.load(f)

RETROARCH_PATH = CONFIG.get("retroarch_path", "retroarch")
SYSTEMS = CONFIG["systems"]

def draw_menu(stdscr, title, options, selected_idx, query=""):
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    stdscr.addstr(1, 2, title, curses.A_BOLD)
    if query:
        stdscr.addstr(2, 2, f"Filter: {query}")
        start_y = 4
    else:
        start_y = 3

    for i, opt in enumerate(options):
        y = start_y + i
        if y >= h - 2:
            break
        if i == selected_idx:
            stdscr.attron(curses.A_REVERSE)
            stdscr.addstr(y, 4, opt)
            stdscr.attroff(curses.A_REVERSE)
        else:
            stdscr.addstr(y, 4, opt)
    stdscr.refresh()

def game_menu(stdscr, system):
    roms_path = os.path.expanduser(system["roms"])
    core_path = os.path.expanduser(system["core"])
    folder_mode = system.get("folder_mode", False)

    try:
        if folder_mode:
            all_entries = sorted([
                d for d in os.listdir(roms_path)
                if os.path.isdir(os.path.join(roms_path, d))
            ])
        else:
            all_entries = sorted([
                f for f in os.listdir(roms_path)
                if os.path.isfile(os.path.join(roms_path, f)) and f.lower().endswith(VALID_EXTS)
            ])
    except FileNotFoundError:
        all_entries = []

    query = ""
    filtered_entries = all_entries
    idx = 0
    scroll = 0

    while True:
        game_list = filtered_entries + ["<< Back"]
        h, w = stdscr.getmaxyx()
        visible_items = h - 5
        scroll = max(0, min(scroll, len(game_list) - visible_items))
        if idx < scroll:
            scroll = idx
        elif idx >= scroll + visible_items:
            scroll = idx - visible_items + 1

        visible_slice = game_list[scroll:scroll + visible_items]
        draw_menu(stdscr, f"{system['name']} Games", visible_slice, idx - scroll, query)

        key = stdscr.getch()

        if key in (curses.KEY_UP, ord('k')):
            idx = (idx - 1) % len(game_list)
        elif key in (curses.KEY_DOWN, ord('j')):
            idx = (idx + 1) % len(game_list)
        elif key == curses.KEY_NPAGE:
            idx = min(idx + visible_items, len(game_list) - 1)
        elif key == curses.KEY_PPAGE:
            idx = max(idx - visible_items, 0)
        elif key == curses.KEY_HOME:
            idx = 0
        elif key == curses.KEY_END:
            idx = len(game_list) - 1
            scroll = max(0, len(game_list) - visible_items)
        elif key in (10, 13):  # Enter
            if idx == len(filtered_entries):  # Back
                return

            if folder_mode:
                rom_dir = os.path.join(roms_path, filtered_entries[idx])
                rom_path = None
                PREFERRED_EXT_ORDER = ('.cue', '.pbp', '.chd', '.iso', '.bin')
                for ext in PREFERRED_EXT_ORDER:
                    for f in sorted(os.listdir(rom_dir)):
                        if f.lower().endswith(ext):
                            rom_path = os.path.join(rom_dir, f)
                            break
                    if rom_path:
                        break
                if not rom_path:
                    curses.endwin()
                    print(f"No valid launchable files found in '{rom_dir}'")
                    input("\nPress Enter to return...")
                    return
            else:
                rom_path = os.path.join(roms_path, filtered_entries[idx])

            curses.endwin()
            cmd = [RETROARCH_PATH, "-L", core_path, rom_path]
            print("\nLaunching:", " ".join(f'"{x}"' if ' ' in x else x for x in cmd))
            try:
                subprocess.run(cmd, check=True)
            except Exception as e:
                print("❌ Failed to launch RetroArch:")
                print(e)
            input("\nPress Enter to return to menu...")
            return
        elif key == 27 or key == ord('q'):
            return
        elif key in (curses.KEY_BACKSPACE, 127, 8):
            query = query[:-1]
        elif 32 <= key <= 126:
            query += chr(key)

        if query.startswith("/"):
            search = query[1:].lower()
            filtered_entries = [f for f in all_entries if search in f.lower()]
        else:
            filtered_entries = [f for f in all_entries if f.lower().startswith(query.lower())]

        if idx >= len(filtered_entries):
            idx = 0

def main_menu(stdscr):
    curses.curs_set(0)

    # Init color pairs
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_WHITE, -1)
    curses.init_pair(2, curses.COLOR_YELLOW, -1)  # Dim orange for core name

    query = ""
    idx = 0

    names_raw = [
        {
            "name": s["name"],
            "core": os.path.basename(os.path.expanduser(s["core"])),
            "display": f'{s["name"]} ({os.path.basename(os.path.expanduser(s["core"]))})',
            "system": s
        }
        for s in SYSTEMS
    ]
    filtered_entries = names_raw

    while True:
        h, w = stdscr.getmaxyx()
        visible_items = h - 6
        scroll = max(0, min(idx - visible_items // 2, len(filtered_entries) - visible_items))
        scroll = max(0, scroll)
        visible_slice = filtered_entries[scroll:scroll + visible_items]

        stdscr.clear()
        stdscr.addstr(0, 2, "RetroArch-TUI Launcher", curses.A_BOLD | curses.A_UNDERLINE)
        #stdscr.addstr(1, 2, "Select System", curses.A_BOLD)
        if query:
            stdscr.addstr(2, 2, f"Filter: {query}")
        for i, entry in enumerate(visible_slice):
            y = 4 + i
            name = entry["name"]
            core = f' ({entry["core"]})'
            if scroll + i == idx:
                stdscr.attron(curses.A_REVERSE)
                stdscr.addstr(y, 4, name)
                stdscr.attron(curses.color_pair(2))
                stdscr.addstr(y, 4 + len(name), core)
                stdscr.attroff(curses.color_pair(2))
                stdscr.attroff(curses.A_REVERSE)
            else:
                stdscr.addstr(y, 4, name)
                stdscr.attron(curses.color_pair(2))
                stdscr.addstr(y, 4 + len(name), core)
                stdscr.attroff(curses.color_pair(2))
        stdscr.addstr(h - 2, 2, "q to quit, r to load retroarch, h for help")
        stdscr.refresh()

        key = stdscr.getch()

        if key in (curses.KEY_UP, ord('k')):
            idx = (idx - 1) % len(filtered_entries)
        elif key in (curses.KEY_DOWN, ord('j')):
            idx = (idx + 1) % len(filtered_entries)
        elif key == curses.KEY_NPAGE:
            idx = min(idx + visible_items, len(filtered_entries) - 1)
        elif key == curses.KEY_PPAGE:
            idx = max(idx - visible_items, 0)
        elif key == curses.KEY_HOME:
            idx = 0
        elif key == curses.KEY_END:
            idx = len(filtered_entries) - 1
        elif key in (10, 13):  # Enter
            selected_system = filtered_entries[idx]["system"]
            game_menu(stdscr, selected_system)
            filtered_entries = [
                e for e in names_raw
                if e["name"].lower().startswith(query.lower())
            ]
        elif key == ord('r'):
            curses.endwin()
            print("\nLaunching RetroArch...")
            try:
                subprocess.run([RETROARCH_PATH], check=True)
            except Exception as e:
                print("❌ Failed to launch RetroArch:")
                print(e)
            input("\nPress Enter to return to menu...")
        elif key == ord('h'):
            show_help(stdscr)
        elif key == 27 or key == ord('q'):
            return
        elif key in (curses.KEY_BACKSPACE, 127, 8):
            query = query[:-1]
        elif 32 <= key <= 126:
            query += chr(key)

        filtered_entries = [
            e for e in names_raw
            if e["name"].lower().startswith(query.lower())
        ]
        if idx >= len(filtered_entries):
            idx = 0

def show_help(stdscr):
    help_text = [
        "RetroArch-TUI Config Help",
        "-------------------------",
        "",
        "Your config.json should look like this:",
        "",
        '{',
        '  "retroarch_path": "retroarch",',
        '  "systems": [',
        '    {',
        '      "name": "SNES",',
        '      "core": "~/.config/retroarch/cores/snes9x_libretro.so",',
        '      "roms": "/mnt/Emulators/roms/snes/roms"',
        '    },',
        '    {',
        '      "name": "PlayStation",',
        '      "core": "~/.config/retroarch/cores/mednafen_psx_hw_libretro.so",',
        '      "roms": "/mnt/Emulators/roms/ps/roms",',
        '      "folder_mode": true',
        '    }',
        '  ]',
        '}',
        "",
        "Controls:",
        "  ↑ ↓ j k     - navigate",
        "  PgUp PgDn   - scroll",
        "  r           - launch RetroArch",
        "  q           - quit",
        "  h           - help (this screen)",
        "",
        "Press any key to return..."
    ]

    stdscr.clear()
    h, w = stdscr.getmaxyx()
    for i, line in enumerate(help_text):
        if i >= h - 1:
            break
        stdscr.addstr(i, 2, line)
    stdscr.refresh()
    stdscr.getch()


if __name__ == "__main__":
    try:
        curses.wrapper(main_menu)
    except Exception:
        curses.endwin()
        print("❌ An error occurred:")
        traceback.print_exc()
        input("\nPress Enter to exit...")

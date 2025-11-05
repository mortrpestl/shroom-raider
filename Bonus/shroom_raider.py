import sys, io, os, json, time
from exit_codes import EXIT_CODES

# Keep stdout/stderr unicode-friendly (was added to support emojis via subprocess)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="ignore")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="ignore")

from Classes.Grid import Grid
from Classes.Entities.Player import Player

ENABLE_TEST_MODE = False
LEVEL_NAME = "TEST"
REPORT_FILE = None
moves_made = 0

def check_win_condition(P, G):
    if P.get_mushroom_count() == G.get_total_mushrooms():
        G.level_clear()

def reset(level, dark_radius=10000):
    global G, P
    G = Grid("test", level, dark_radius=dark_radius)
    P = G.get_player()
    return G, P

def parser(instructions, P: Player, G: Grid, level, reset_only):
    global moves_made
    item_here, holding_anything = "No items here", None

    if instructions is None:
        return item_here, holding_anything

    if isinstance(instructions, str):
        lines = instructions.splitlines() if "\n" in instructions else [instructions]
    else:
        lines = list(instructions)

    for line in lines:
        for inst in line:
            inst = inst.lower()

            if ENABLE_TEST_MODE and inst == "?":
                # write some debug outputs and exit
                with open("output_debug.txt","w",encoding="utf-8") as f:
                    f.write("CLEAR\n" if G.get_is_cleared() else "NO CLEAR\n")
                    f.write(G.get_vis_map_as_str())
                exit(EXIT_CODES["quit"])

            # non-WASDP inputs
            if inst == "q":
                print("Quitting to main menu...", flush=True)
                time.sleep(1.5)
                exit(EXIT_CODES["quit"])
            if inst == "!":
                G, P = reset(level, dark_radius=G.get_dark_radius())
            if reset_only:
                break
            if inst not in "wasdpf!":
                break

            # WASDP inputs
            if inst in "wasd":
                moved = P.set_pos(inst)
                if moved: moves_made += 1
            elif inst == "p": P.collect_item()
            elif inst == "f": P.use_item()

            # mushroom collection
            if shroom := P.get_above_mushroom():
                shroom.collect(P)

            # water kills
            if P.get_above_water():
                P.destroy()
                P.kill()

            # win/loss check
            check_win_condition(P, G)
            if G.get_is_cleared() or P.get_is_dead():
                break

    # update UI strings
    holding_anything = f"Holding item {P.get_item().__class__.__name__}" if P.get_item() else None
    item_here = f"Above item {P.get_above_item()}" if P.get_above_item() else "No items here"

    return item_here, holding_anything

def write_report(G, P, win: bool, dead: bool):
    global REPORT_FILE, moves_made
    if not REPORT_FILE:
        return
    try:
        payload = {
            "mushrooms_collected": P.get_mushroom_count(),
            "moves_made": moves_made,
            "win": bool(win),
            "dead": bool(dead)
        }
        tmp = REPORT_FILE + ".tmp"
        with open(tmp,"w",encoding="utf-8") as f:
            json.dump(payload,f)
            f.flush(); os.fsync(f.fileno())
        try:
            os.replace(tmp, REPORT_FILE)
        except Exception:
            with open(REPORT_FILE,"w",encoding="utf-8") as f:
                json.dump(payload,f)
    except Exception as e:
        print(f"Failed to write report file {REPORT_FILE}: {e}")

"""
NOTE: 

Since shroom_raider.py here cannot be run (by the player) without MainMenu.py, I removed some unnecessary code (like having the args as its own if-statement, because now that is the default).

args will always be used by default

-R to assist in storing session statistics
-dark-radius to darken if there is a provided 'dark' param in the sheet
"""


def main():
    global G, P, REPORT_FILE, moves_made

    args = sys.argv[1:]
    dark_radius = 10000

    # handle optional args
    if "-R" in args:
        idx = args.index("-R")
        if idx + 1 < len(args):
            REPORT_FILE = args[idx+1]
            args = args[:idx] + args[idx+2:]
    if "--dark" in args:
        idx = args.index("--dark")
        if idx + 1 < len(args):
            try:
                dark_radius = int(args[idx+1])
            except ValueError:
                pass
            args = args[:idx] + args[idx+2:]

    if not args:
        # interactive default: read TEST.txt next to this script
        with open(f"{LEVEL_NAME}.txt", encoding="utf-8") as lvl_file:
            first_line = lvl_file.readline().lstrip("\ufeff")
            r,c = map(int, first_line.split())
            level = lvl_file.read()
        G = Grid(LEVEL_NAME, level)
        P = G.get_player()
        check_win_condition(P, G)
        item_here, holding_anything = "No items here", None
        stop_or_reset_only = G.render(P, G, item_here, holding_anything, test_mode=ENABLE_TEST_MODE)
        while True:
            item_here, holding_anything = parser(input(), P, G, level, stop_or_reset_only)
            try:
                stop_or_reset_only = G.render(P, G, item_here, holding_anything, test_mode=ENABLE_TEST_MODE)
            except Exception:
                stop_or_reset_only = False
            if G.get_is_cleared():
                print("CLEAR")
                write_report(G, P, True, False)
                sys.exit(EXIT_CODES["victory"])
            if P.get_is_dead():
                print("DEAD")
                write_report(G, P, False, True)
                sys.exit(EXIT_CODES["defeat"])
        return

    # file-based
    if args[0] == "-f" and len(args) >= 2:
        stage_file = args[1]
        with open(stage_file, encoding="utf-8") as lvl_file:
            first_line = lvl_file.readline().lstrip("\ufeff")
            r,c = map(int, first_line.split())
            level = lvl_file.read()
        G = Grid(stage_file, level, dark_radius=dark_radius)
        P = G.get_player()
        check_win_condition(P, G)

        # possible input 1: -f <stage_file> (interactive manual mode)
        if len(args) == 2:
            item_here, holding_anything = "No items here", None
            stop_or_reset_only = G.render(P, G, item_here, holding_anything, test_mode=ENABLE_TEST_MODE)
            while True:
                item_here, holding_anything = parser(input(), P, G, level, stop_or_reset_only)
                try:
                    stop_or_reset_only = G.render(P, G, item_here, holding_anything, test_mode=ENABLE_TEST_MODE)
                except Exception:
                    stop_or_reset_only = False
                if G.get_is_cleared():
                    write_report(G, P, True, False)
                    sys.exit(EXIT_CODES["victory"])
                if P.get_is_dead():
                    write_report(G, P, False, True)
                    sys.exit(EXIT_CODES["defeat"])
        else:
            print("Invalid arguments. Use -f <stage_file> or interactive mode")
    else:
        print("Invalid arguments. Use -f <stage_file> or interactive mode")

if __name__ == "__main__":
    P,G = None,None
    if ENABLE_TEST_MODE:
        # test-mode logging setup (unchanged)
        os.makedirs("Logs",exist_ok=True)
    main()
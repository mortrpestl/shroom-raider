import sys, io, os, json, time
from argparse import ArgumentParser as ap
import Utils.sounds as s
from exit_codes import EXIT_CODES

# Keep stdout/stderr unicode-friendly (was added to support emojis via subprocess)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="ignore")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="ignore")

from Classes.Grid import Grid
from Classes.Entities.Player import Player

ENABLE_TEST_MODE = False
LEVEL_NAME = "Levels/TEST"
REPORT_FILE = None
MOVES_MADE = 0

def check_win_condition(P, G):
    if P.get_mushroom_count() == G.get_total_mushrooms():
        G.level_clear()

def reset(level, dark_radius=None):
    global G, P
    G = Grid("test", level, dark_radius=dark_radius)
    P = G.get_player()
    return G, P

def parser(instructions, P: Player, G: Grid, level, reset_only):
    global MOVES_MADE

    if instructions is None: return

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
                if moved: MOVES_MADE += 1
            elif inst == "p": P.collect_item()
            elif inst == "f": P.use_item()

            # mushroom collection
            P.collect_shroom()

            # win/loss check
            check_win_condition(P, G)
            if G.get_is_cleared() or P.get_is_dead():
                break

def write_report(G, P, win: bool, dead: bool):
    global REPORT_FILE, MOVES_MADE
    if not REPORT_FILE:
        return
    try:
        payload = {
            "mushrooms_collected": P.get_mushroom_count(),
            "moves_made": MOVES_MADE,
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
    global G, P, REPORT_FILE, MOVES_MADE

    argument_parser = ap()
    argument_parser.add_argument('-f', '--stage_file')
    argument_parser.add_argument('-d', '--darkness_radius', default=None)
    argument_parser.add_argument('-R', '--report_file', default=None)
    args = argument_parser.parse_args()

    # optional args
    REPORT_FILE = args.report_file
    try:
        dark_radius = int(args.darkness_radius)
    except Exception:
        dark_radius = None

    if args.stage_file == None: # default interactive mode
        with open(f"{LEVEL_NAME}.txt", encoding="utf-8") as lvl_file:
            first_line = lvl_file.readline().lstrip("\ufeff")
            r,c = map(int, first_line.split())
            level = lvl_file.read()

        G = Grid(LEVEL_NAME, level)
        P = G.get_player()

        check_win_condition(P, G)

        stop_or_reset_only = G.render(P, test_mode=ENABLE_TEST_MODE)

        while True:
            parser(input(), P, G, level, stop_or_reset_only)
            try:
                stop_or_reset_only = G.render(P, test_mode=ENABLE_TEST_MODE)
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

    # file-based
    if args.stage_file != None:

        with open(args.stage_file, encoding="utf-8") as lvl_file:
            first_line = lvl_file.readline().lstrip("\ufeff")
            r,c = map(int, first_line.split())
            level = lvl_file.read()

        G = Grid(args.stage_file, level, dark_radius)
        P = G.get_player()
        check_win_condition(P, G)

        stop_or_reset_only = G.render(P, test_mode=ENABLE_TEST_MODE)

        while True:
            parser(input(), P, G, level, stop_or_reset_only)
            try:
                stop_or_reset_only = G.render(P, test_mode=ENABLE_TEST_MODE)
            except Exception:
                stop_or_reset_only = False
            if G.get_is_cleared():
                write_report(G, P, True, False)
                sys.exit(EXIT_CODES["victory"])
            if P.get_is_dead():
                write_report(G, P, False, True)
                sys.exit(EXIT_CODES["defeat"])

if __name__ == "__main__":
    s.initAll()

    P,G = None,None
    if ENABLE_TEST_MODE:
        # test-mode logging setup (unchanged)
        os.makedirs("Logs",exist_ok=True)
    main()
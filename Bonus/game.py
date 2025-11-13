import sys
import io
import os
import json
from argparse import ArgumentParser as ap
import Utils.sounds as s
import Utils.movement as m
from Utils.Enums import ExitCodes

from Classes.Grid import Grid
from Classes.Entities.Player import Player
from Classes.Entities.Bomb import Bomb

from Utils.general_utils import wait

# Keep stdout/stderr unicode-friendly (was added to support emojis via subprocess)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="ignore")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="ignore")

ENABLE_TEST_MODE = False
LEVEL_NAME = "Levels/TEST"
REPORT_FILE = None
MOVES_MADE = 0
ACTIVE = False


def check_win_condition(P, G):
    if P.get_mushroom_count() == G.get_total_mushrooms():
        G.level_clear()


def reset(level, metadata=None):
    global G, P
    G = Grid("test", level, metadata=metadata)
    P = G.get_player()
    return G, P


def parser(inst, P: Player, G: Grid, level, reset_only):
    global MOVES_MADE

    if ENABLE_TEST_MODE and inst == "?":
        # write some debug outputs and exit
        with open("output_debug.txt", "w", encoding="utf-8") as f:
            f.write("CLEAR\n" if G.get_is_cleared() else "NO CLEAR\n")
            f.write(G.get_vis_map_as_str())
        exit(ExitCodes.QUIT.value)

    # non-WASDP inputs
    if inst == "Q":
        print("Quitting level...", flush=True)
        wait(2)
        exit(ExitCodes.QUIT.value)

    if inst == "!":
        G, P = reset(level, metadata=G.get_metadata())

    if reset_only:
        return

    # WASDP inputs
    if inst in "wasd":
        moved = P.set_pos(inst)
        if moved:
            MOVES_MADE += 1
    elif inst == "p":
        if P.get_item() is None:
            P.collect_item()
        elif isinstance(P.get_item(), Bomb) and isinstance(P.get_entity_below(), Bomb):
            P.collect_item()
        else:
            return  # no overwriting items
    elif inst == "f":
        P.use_item()

    # mushroom collection
    P.collect_shroom()

    # win/loss check
    check_win_condition(P, G)
    if G.get_is_cleared() or P.get_is_dead():
        return


def write_report(G, P, win: bool, dead: bool):
    global REPORT_FILE, MOVES_MADE
    if not REPORT_FILE:
        return
    try:
        payload = {
            "mushrooms_collected": P.get_mushroom_count(),
            "moves_made": MOVES_MADE,
            "win": bool(win),
            "dead": bool(dead),
        }
        tmp = REPORT_FILE + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(payload, f)
            f.flush()
            os.fsync(f.fileno())
        try:
            os.replace(tmp, REPORT_FILE)
        except Exception:
            with open(REPORT_FILE, "w", encoding="utf-8") as f:
                json.dump(payload, f)
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

    DEFAULT_DARK = 10000
    DEFAULT_BEE = "3 3"

    argument_parser = ap()
    argument_parser.add_argument("-f", "--stage_file")
    argument_parser.add_argument("-R", "--report_file", default=None)
    argument_parser.add_argument("-d", "--darkness_radius", default=DEFAULT_DARK)
    argument_parser.add_argument("-B", "--bee_data", default=DEFAULT_BEE)
    args = argument_parser.parse_args()

    REPORT_FILE = args.report_file

    try:
        dark_radius = int(args.darkness_radius)
    except Exception:
        dark_radius = None

    bee_data = args.bee_data

    m.block_keys()

    metadata = {"dark_radius": dark_radius, "bee_data": bee_data}

    with open(args.stage_file, encoding="utf-8") as lvl_file:
        first_line = lvl_file.readline().lstrip("\ufeff")
        r, c = map(int, first_line.split())
        level = lvl_file.read()

        print()
        G = Grid(args.stage_file, level, metadata=metadata)
        P = G.get_player()
        check_win_condition(P, G)

        stop_or_reset_only = G.render(test_mode=ENABLE_TEST_MODE, f=True)

        while True:
            key_input = m.check_movement()
            if key_input is not None:
                parser(key_input, P, G, level, stop_or_reset_only)
                try:
                    stop_or_reset_only = G.render(test_mode=ENABLE_TEST_MODE)
                except Exception:
                    stop_or_reset_only = False

                if G.get_is_cleared():
                    print("CLEAR")
                    write_report(G, P, True, False)
                    wait(1)
                    sys.exit(ExitCodes.VICTORY.value)
                if P.get_is_dead():
                    print("DEAD")
                    write_report(G, P, False, True)
                    wait(1)
                    sys.exit(ExitCodes.DEFEAT.value)


if __name__ == "__main__":
    s.initAll()

    P, G = None, None
    if ENABLE_TEST_MODE:
        # test-mode logging setup (unchanged)
        os.makedirs("Logs", exist_ok=True)
    main()

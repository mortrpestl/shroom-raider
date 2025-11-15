import io
import json
import os
import pathlib
import sys
from argparse import ArgumentParser as ap

import Utils.movement as m
import Utils.sounds as s
from Classes.Entities.Bomb import Bomb
from Classes.Entities.Player import Player
from Classes.Grid import Grid
from colorama import Fore
from Utils.animator import load_in, progress_bar, typewriter
from Utils.Enums import ExitCodes

# Keep stdout/stderr unicode-friendly (was added to support emojis via subprocess)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="ignore")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="ignore")

ENABLE_TEST_MODE = False
LEVEL_NAME = "Levels/TEST"
REPORT_FILE = None
MOVES_MADE = 0
ACTIVE = False


def check_win_condition(P: Player, G: Grid):
    """Checks if a player has met the win condition of a grid

    Args:
        P: A Player Entity
        G: A Grid object

    """
    if P.get_mushroom_count() == G.get_total_mushrooms():
        G.level_clear()


def reset(level: str, metadata: dict):
    """Resets a stage to its starting conditions

    Args:
        level: A string representation of the stage being reset
        metadata: A dict of attributes representing specific grid configurations (e.g. bee lag, bee count)

    Returns:
        A Grid object that contains the reset level, and a Player entity on that Grid

    """
    global G, P
    G = Grid("test", level, metadata=metadata)
    P = G.get_player()
    return G, P


def parser(inst: str, P: Player, G: Grid, level: str, reset_only: bool):
    """Parses user inputs to play game. Also updates global movecounter for the current game.

    Args:
        instructions: The given input string of the player's moves
        P: The current Player entity
        G: The current Grid object
        level: A string representation of the ORIGINAL stage
        reset_only: A boolean indicating if moves other than reset can be played

    """
    global MOVES_MADE

    if ENABLE_TEST_MODE and inst == "?":
        # write some debug outputs and exit
        with open("output_debug.txt", "w", encoding="utf-8") as f:
            f.write("CLEAR\n" if G.get_is_cleared() else "NO CLEAR\n")
            f.write(G.get_vis_map_as_str())
        exit(ExitCodes.QUIT.value)

    # non-WASDP inputs
    if inst == "Q":
        progress_bar("Quitting Level", total_time=2)
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
        if P.get_item() is None or (isinstance(P.get_item(), Bomb) and isinstance(P.get_entity_below(), Bomb)):
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


def write_report(G: Grid, P: Player, win: bool, dead: bool):
    """Creates a report of the played game after completion of a level.

    Args:
        P: The current Player entity
        G: The current Grid object
        win, dead: Indicate whether the player has won the game or has died

    """
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
            pathlib.Path(tmp).replace(REPORT_FILE)
        except Exception:
            with open(REPORT_FILE, "w", encoding="utf-8") as f:
                json.dump(payload, f)
    except Exception as e:
        print(f"Failed to write report file {REPORT_FILE}: {e}")


def main():
    """The main game logic for Shroom Raider
    -> Processes Command Line Arguments
    -> Handles Game Loop
    """
    global G, P, REPORT_FILE, MOVES_MADE

    DEFAULT_DARK = 10000
    DEFAULT_BEE = "3 3"

    argument_parser = ap()
    argument_parser.add_argument("-f", "--stage_file")
    argument_parser.add_argument("-R", "--report_file", default=None)
    argument_parser.add_argument("-d", "--darkness_radius", default=DEFAULT_DARK)
    argument_parser.add_argument("-B", "--bee_data", default=DEFAULT_BEE)
    argument_parser.add_argument("-M", "--bgm", default="default-level-music.mp3")
    args = argument_parser.parse_args()

    REPORT_FILE = args.report_file

    try:
        dark_radius = int(args.darkness_radius)
    except Exception:
        dark_radius = None

    bee_data = args.bee_data

    m.block_keys()
    
    metadata = {"dark_radius": dark_radius, "bee_data": bee_data}

    s.level_bgm_sound(args.bgm)

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
                    G.render(test_mode=ENABLE_TEST_MODE)

                    s.current_bgm_stop()
                    s.victory_sound()

                    with open("Assets/UI/ClearText.txt", encoding="utf+8") as text:
                        load_in("\n" + text.read(), 2, colors=[Fore.GREEN], fx_map="✩･ﾟ.")
                    typewriter("Way to go! Onto the next area...", colors=[Fore.GREEN])
                    write_report(G, P, True, False)
                    progress_bar("\nTaking you to main menu...", 2)
                    sys.exit(ExitCodes.VICTORY.value)
                if P.get_is_dead():
                    # G.render(test_mode=ENABLE_TEST_MODE)
                    
                    s.current_bgm_stop()
                    s.defeat_sound()

                    with open("Assets/UI/DefeatText.txt", encoding="utf-8") as text:
                        load_in("\n" + text.read(), 2, colors=[Fore.RED], fx_map="Xx.")
                    typewriter("Don't give up yet! There're still shrooms to raid...", colors=[Fore.RED])
                    write_report(G, P, False, True)
                    progress_bar("\nTaking you to main menu...", 2)
                    sys.exit(ExitCodes.DEFEAT.value)


if __name__ == "__main__":
    s.initAll()

    P, G = None, None
    if ENABLE_TEST_MODE:
        # test-mode logging setup (unchanged)
        pathlib.Path("Logs").mkdir(exist_ok=True, parents=True)
    main()
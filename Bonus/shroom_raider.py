import os
import sys
import subprocess
import tempfile
import json
import time
import LevelManager
from argparse import ArgumentParser as ap

from Bonus_Classes.PlayerData import Data
from Bonus_Classes.Leaderboard import (
    show_personal_leaderboard,
    show_general_leaderboard,
    show_level_leaderboard,
)
from exit_codes import EXIT_CODES

HERE = os.path.dirname(__file__)
SHROOM_SCRIPT = os.path.join(HERE, "game.py")

# * Helper Functions


def clear_terminal():
    os.system("cls" if os.name == "nt" else "clear")


def wait(seconds):
    time.sleep(seconds)


def print_and_wait(message, seconds=1):
    print(message)
    wait(seconds)
    clear_terminal()


<<<<<<< HEAD
def parser(inst, P: Player, G: Grid, level, reset_only):
    global MOVES_MADE

    if ENABLE_TEST_MODE and inst == "?":
        # write some debug outputs and exit
        with open("output_debug.txt", "w", encoding="utf-8") as f:
            f.write("CLEAR\n" if G.get_is_cleared() else "NO CLEAR\n")
            f.write(G.get_vis_map_as_str())
        exit(EXIT_CODES["quit"])

    # non-WASDP inputs
    if inst == "Q":
        print("Quitting to main menu...", flush=True)
        time.sleep(1.5)
        exit(EXIT_CODES["quit"])

    if inst == "!":
        G, P = reset(level, dark_radius=G.get_dark_radius())

    if reset_only:
        return

    # WASDP inputs
    if inst in "wasd":
        moved = P.set_pos(inst)
        if moved: MOVES_MADE += 1
    elif inst == "p" and P.get_item() is None: P.collect_item()
    elif inst == "f": P.use_item()

    # mushroom collection
    P.collect_shroom()

    # win/loss check
    check_win_condition(P, G)
    if G.get_is_cleared() or P.get_is_dead():
        return
=======
# * Advanced Helper Functions
>>>>>>> 8d8cd90d9b064483b7bec962c82d862a0135c935


def show_statistics(pdata):
    if pdata is None:
        print("No statistics available.")
    else:
        print("\nPlayer statistics:")
        print(pdata)


# * Level List Helper Functions


def print_levels_table(levels):
    """
    Print a summary of the levels.
    """

    headers = ["ID", "Title", "Description", "Difficulty"]
    rows = []
    for lvl in levels:
        rows.append(
            [
                str(lvl.get("id", "")),
                str(lvl.get("title", "")),
                str(lvl.get("description", "")).replace("\n", " "),
                str(lvl.get("difficulty", "Normal")),
            ]
        )

    col_widths = []
    for i, h in enumerate(headers):
        max_cell = max(len(row[i]) for row in rows)
        col_widths.append(max(len(h), max_cell))

    header_line = " | ".join(h.ljust(col_widths[i]) for i, h in enumerate(headers))
    inner_width = len(header_line) + 2

    print("+" + "-" * inner_width + "+")  # top
    print(f"| {header_line} |")
    print("|" + "-" * inner_width + "|")

    for row in rows:
        row_line = " | ".join(row[i].ljust(col_widths[i]) for i in range(len(headers)))
        print(f"| {row_line} |")

    print("+" + "-" * inner_width + "+")  # bottom


# * Level Selection and Launching Functions


def choose_level(levels):
    """
    Displays Level Select menu and returns chosen level dict or None on quit.
    """

    # if no levels
    clear_terminal()
    if not levels:
        print("No levels found in Levels/")
        return None

    # if there is levels
    print("""
+-------------------------+
|      LEVEL SELECT       |
+-------------------------+
""")
    while True:
        print_levels_table(levels)
        choice = input("Select level ID or number (or 'q' to quit): ").strip()
        if choice == "q":
            return "q"
        if choice.isdigit():
            n = int(choice)
            for lvl in levels:
                if lvl.get("id") == n:
                    return lvl
            if 1 <= n <= len(levels):
                return levels[n - 1]

        print("Invalid choice.")
        wait(1)
        clear_terminal()


def make_stage_file_from_grid(grid_text):
    """
    Creates: the file to send to shroom_raider.py from grid_text.
    Returns: path to this temporary file, for sending to shroom_raider.py
    """
    if not grid_text.strip():
        raise ValueError("Empty grid")

    content = grid_text.strip() + "\n"
    fd, path = tempfile.mkstemp(prefix="stage_", suffix=".txt", dir=HERE)
    os.close(fd)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return path


def launch_game_with_level(level):
    """
    Send the level to shroom_raider.py
    """
    # create temp files to store level
    stage_path = make_stage_file_from_grid(level["grid"])
    report_fd, report_path = tempfile.mkstemp(
        prefix="shroom_report_", suffix=".json", dir=HERE
    )
    os.close(report_fd)

    try:
        # run game
        cmd = [sys.executable, SHROOM_SCRIPT, "-f", stage_path, "-R", report_path]

        # optional dark mode parameter
        if "dark_radius" in level:
            cmd += ["-d", str(level["dark_radius"])]

        print(f"\nRunning: {' '.join(cmd)}\n")
        return_code = subprocess.call(cmd)

        # load report
        report = None
        if os.path.getsize(report_path) > 0:
            with open(report_path, "r", encoding="utf-8") as f:
                report = json.load(f)
        return return_code, report
    finally:
        # cleans up temp files
        for path in (stage_path, report_path):
            if os.path.exists(path):
                os.remove(path)

# gameplay start + loop
def main():
    print("""
+------------------------+
|WELCOME TO SHROOM RAIDER|
+------------------------+
          """)

    username = (
        input("Username (Input nothing to enter as 'guest'): ").strip() or "GUEST"
    )
    pdata = Data(username)

    while True:
        levels = LevelManager.load_levels()
        lvl = choose_level(levels)

        if lvl == "q":
            print("Quitting launcher.")
            exit(EXIT_CODES["quit"])

        while True:
            # session start
            start_time = time.time()
            return_code, report = launch_game_with_level(lvl)
            end_time = time.time()
            wait(1.25)
            clear_terminal()
            # session end

            # process session data
            if report:
                elapsed_time = float(end_time - start_time)
                pdata.apply_report_dict(
                    report,
                    return_code=return_code,
                    level_id=lvl["id"],
                    elapsed_time=elapsed_time,
                )

            while True:
                # the gameloop
                print("""
            +---------------------------+
            |      LEVEL PROCESSED      |
            +---------------------------+
            | r - Replay Level          |
            | m - Return to Main Menu   |
            | s - View Statistics       |
            | p - Personal Leaderboard  |
            | g - General Leaderboard   |
            | l - Level Leaderboard     |
            | q - Quit Launcher         |
            +---------------------------+
            """)

                choice = input("Choose your option: ").strip().lower()
                clear_terminal()
                match choice:
                    case "r" | "m":
                        break
                    case "s":
                        show_statistics(pdata)
                        continue
                    case "q":
                        print("Quitting launcher.")
                        exit(EXIT_CODES["quit"])
                    case "p":
                        show_personal_leaderboard(pdata)
                        continue
                    case "g":
                        show_general_leaderboard()
                        continue
                    case "l":
                        show_level_leaderboard(lvl["id"])
                        continue
                    case _:
                        print("Invalid choice, try again.")

            if choice in ("r", "replay"):
                continue  # continue playing the level
            if choice in ("m", "menu"):  # stop and go back to menu
                clear_terminal()
                break


if __name__ == "__main__":
    argument_parser = ap()
    argument_parser.add_argument("-f", "--stage_file")
    argument_parser.add_argument("-d", "--darkness_radius", default=None)
    argument_parser.add_argument("-R", "--report_file", default=None)
    args = argument_parser.parse_args()

    if args.stage_file is not None:

        cmd = [sys.executable, SHROOM_SCRIPT, "-f", args.stage_file]

        # optional dark mode parameter
        if args.darkness_radius is not None:
            cmd += ["-d", str(args.darkness_radius)]

        # optional report parameter
        if args.report_file is not None:
            cmd += ["-R", str(args.report_file)]

        print(f"\nRunning: {' '.join(cmd)}\n")
        return_code = subprocess.call(cmd)

    else:
        main()

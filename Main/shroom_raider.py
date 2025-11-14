#!/usr/bin/env python3
import sys
import io
import os
from argparse import ArgumentParser as ap
from Classes.Grid import Grid
from Classes.Entities.Player import Player

# ! the 2 lines of code below were written with AI assistance
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="ignore")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="ignore")


ENABLE_TEST_MODE = False  # toggle if you want to get logs; for testing
LEVEL_NAME = "TEST"


def check_win_condition(P: Player, G: Grid):
    """Checks if a player has met the win condition of a grid

    Args:
        P: A Player Entity
        G: A Grid object
    """

    if P.get_mushroom_count() == G.get_total_mushrooms():
        G.level_clear()


def reset(level: str):
    """Resets a stage to its starting conditions

    Args:
        level: A string representation of the stage being reset

    Returns:
        A Grid object that contains the reset level, and a Player entity on that Grid
    """
    global G, P
    G = Grid("test", level)
    P = G.get_player()
    return G, P


def parser(instructions: str, P: Player, G: Grid, level: str, reset_only: bool):
    """Parses user inputs to play game

    Args:
        instructions: The given input string of the player's moves
        P: The current Player entity
        G: The current Grid object
        level: A string representation of the ORIGINAL stage
        reset_only: A boolean indicating if moves other than reset can be played
    """
    global item_here, holding_anything

    if instructions is None:
        return

    if isinstance(instructions, str):
        lines = instructions.splitlines() if "\n" in instructions else [instructions]
    else:
        lines = list(instructions)

    if ENABLE_TEST_MODE:
        with open(INPUT_LOG_FILE, "a", encoding="utf-8") as f:
            for ln in lines:
                if ln != "?":
                    f.write(str(ln) + "\n")

    for line in lines:
        for inst in line:
            inst = inst.lower()

            if ENABLE_TEST_MODE and inst == "?":
                with open(OUTPUT_LOG_FILE, "w", encoding="utf-8") as f:
                    f.write("CLEAR\n" if G.get_is_cleared() else "NO CLEAR\n")
                    f.write(G.get_vis_map_as_str())
                exit()

            if inst == "!":
                G, P = reset(level)

            if reset_only:
                break

            if G.get_is_cleared() or P.get_is_dead():
                break

            if inst not in "wasdp!":
                break

            if inst in "wasd":
                P.set_pos(inst)
            elif inst == "p":
                if P.get_item() is None:
                    P.collect_item()

            P.collect_shroom()  # if applicable

            check_win_condition(P, G)


def main():
    """The main game logic for Shroom Raider
    -> Processes Command Line Arguments
    -> Handles Game Loop
    """
    global G, P

    argument_parser = ap()
    argument_parser.add_argument("-f", "--stage_file")
    argument_parser.add_argument("-m", "--movement_file")
    argument_parser.add_argument("-o", "--output_file")
    args = argument_parser.parse_args()

    if args.stage_file is None:
        with open(f"{LEVEL_NAME}.txt", encoding="utf-8") as lvl_file:
            first_line = lvl_file.readline().lstrip("\ufeff")
            r, c = map(int, first_line.split())
            level = lvl_file.read()

        G = Grid(LEVEL_NAME, level)
        P = G.get_player()

        check_win_condition(P, G)

        while True:
            stop_or_reset_only = G.render(P, test_mode=ENABLE_TEST_MODE)
            if stop_or_reset_only:
                exit()
            # each input() returns one line; parser will process that line
            parser(input(), P, G, level, stop_or_reset_only)

    elif args.stage_file is not None:
        with open(args.stage_file, encoding="utf-8") as lvl_file:
            first_line = lvl_file.readline().lstrip("\ufeff")
            r, c = map(int, first_line.split())
            level = lvl_file.read()

        G = Grid("UserInput", level)
        P = G.get_player()

        check_win_condition(P, G)

        if args.movement_file is None or args.output_file is None:
            while True:
                stop_or_reset_only = G.render(P, test_mode=ENABLE_TEST_MODE)
                if stop_or_reset_only:
                    exit()
                parser(input(), P, G, level, stop_or_reset_only)

        elif args.movement_file is not None and args.output_file is not None:
            parser(args.movement_file, P, G, level, reset_only=False)

            with open(args.output_file, "w", encoding="utf-8") as f:
                f.write(f"{r} {c}\n")
                if P.get_mushroom_count() == G.get_total_mushrooms():
                    f.write("CLEAR\n")
                else:
                    f.write("NO CLEAR\n")
                f.write(G.get_vis_map_as_str())

        else:  # this is just for safety
            print(
                "Invalid arguments. Usage:\n"
                "python3 shroom_raider.py -f <stage_file>\n"
                "python3 shroom_raider.py -f <stage_file> -m <moves> -o <output_file>"
            )
    else:
        print("Invalid arguments. Use -f <stage_file> or -f <stage_file> -m <moves> -o <output_file>")


if __name__ == "__main__":
    P, G = None, None
    item_here = "No items here"
    holding_anything = None

    if ENABLE_TEST_MODE:
        base_folder = "Logs"
        os.makedirs(base_folder, exist_ok=True)

        existing = [d for d in os.listdir(base_folder) if os.path.isdir(os.path.join(base_folder, d)) and d.isdigit()]
        run_number = max([int(d) for d in existing], default=0) + 1

        run_folder = os.path.join(base_folder, str(run_number))
        os.makedirs(run_folder)

        with (
            open(f"{LEVEL_NAME}.txt", encoding="utf-8") as src,
            open(os.path.join(run_folder, "map.txt"), "w", encoding="utf-8") as dst,
        ):
            dst.write(src.read())

        INPUT_LOG_FILE = os.path.join(run_folder, "input.txt")
        OUTPUT_LOG_FILE = os.path.join(run_folder, "output.txt")

    main()

# * RUFF CHECKED: 2 ERRORS LEFT (12/10/2025 7:54 PM)

import io
import sys
from argparse import ArgumentParser

from classes.entities.player import Player
from classes.grid import Grid

# ! the 2 lines of code below were written with AI assistance
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="ignore")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="ignore")


LEVEL_NAME = "TEST"


def check_win_condition(p: Player, g: Grid) -> None:
    """Check if a player has met the win condition of a grid.

    Marks the current grid as cleared if player has met the win conditions

    Args:
        p (Player): The player being checked
        g (Grid): The grid that contains the player

    """
    if p.get_mushroom_count() == g.get_total_mushrooms():
        g.level_clear()


def reset(level: str) -> tuple[Grid, Player]:
    """Reset a stage to its starting conditions.

    Args:
        level: A string representation of the stage being reset

    Returns:
        A Grid object that contains the reset level, and a Player entity on that Grid.

    """
    g = Grid("test", level)
    p = g.get_player()
    # update module-level names exactly as before
    globals()["G"], globals()["P"] = g, p
    return g, p


def parser(instructions: str, p: Player, g: Grid, level: str, *, reset_only: bool) -> None:
    """Parse user inputs to play game.

    Args:
        instructions: The given input string of the player's moves
        p: The current Player entity
        g: The current Grid object
        level: A string representation of the ORIGINAL stage
        reset_only: A boolean indicating if moves other than reset can be played

    """
    # preserve original globals usage (only declare if you intend to assign)
    # item_here and holding_anything are read-only in this function in original code
    if instructions is None:
        return

    if isinstance(instructions, str):
        lines = instructions.splitlines() if "\n" in instructions else [instructions]
    else:
        lines = list(instructions)

    for line in lines:
        for ch in line:
            inst = ch.lower()

            if inst == "!":
                g, p = reset(level)

            if (reset_only) or (g.get_is_cleared() or p.get_is_dead()) or (inst not in "wasdp!"):
                break

            if inst in "wasd":
                p.set_pos(inst)
            elif inst == "p" and p.get_item() is None:
                p.collect_item()

            p.collect_shroom()  # if applicable

            check_win_condition(p, g)


def main() -> None:
    """Run the main game logic for Shroom Raider.

    -> Processes Command Line Arguments
    -> Handles Game Loop
    """
    argument_parser = ArgumentParser()
    argument_parser.add_argument("-f", "--stage_file")
    argument_parser.add_argument("-m", "--movement_file")
    argument_parser.add_argument("-o", "--output_file")
    args = argument_parser.parse_args()

    if args.stage_file is None:
        with open(f"{LEVEL_NAME}.txt", encoding="utf-8") as lvl_file:
            first_line = lvl_file.readline().lstrip("\ufeff")
            r, c = map(int, first_line.split())
            level = lvl_file.read()

        # assign module-level names exactly as original
        globals()["G"] = Grid(LEVEL_NAME, level)
        globals()["P"] = globals()["G"].get_player()

        check_win_condition(globals()["P"], globals()["G"])

        while True:
            stop_or_reset_only = globals()["G"].render(globals()["P"])
            if stop_or_reset_only:
                sys.exit()
            # each input() returns one line; parser will process that line
            parser(input(), globals()["P"], globals()["G"], level, reset_only=stop_or_reset_only)

    elif args.stage_file is not None:
        with open(args.stage_file, encoding="utf-8") as lvl_file:
            first_line = lvl_file.readline().lstrip("\ufeff")
            r, c = map(int, first_line.split())
            level = lvl_file.read()

        globals()["G"] = Grid("UserInput", level)
        globals()["P"] = globals()["G"].get_player()

        check_win_condition(globals()["P"], globals()["G"])

        if args.movement_file is None or args.output_file is None:
            while True:
                stop_or_reset_only = globals()["G"].render(globals()["P"])
                if stop_or_reset_only:
                    sys.exit()
                parser(input(), globals()["P"], globals()["G"], level, reset_only=stop_or_reset_only)

        elif args.movement_file is not None and args.output_file is not None:
            # original behavior: parser received movement argument as-is (tests sometimes pass raw move strings)
            parser(args.movement_file, globals()["P"], globals()["G"], level, reset_only=False)

            with open(args.output_file, "w", encoding="utf-8") as f:
                f.write(f"{r} {c}\n")
                if globals()["P"].get_mushroom_count() == globals()["G"].get_total_mushrooms():
                    f.write("CLEAR\n")
                else:
                    f.write("NO CLEAR\n")
                f.write(globals()["G"].get_vis_map_as_str())

        else:  # this is just for safety
            print(
                "Invalid arguments. Usage:\n"
                "python3 shroom_raider.py -f <stage_file>\n"
                "python3 shroom_raider.py -f <stage_file> -m <moves> -o <output_file>",
            )
    else:
        print("Invalid arguments. Use -f <stage_file> or -f <stage_file> -m <moves> -o <output_file>")


if __name__ == "__main__":
    P, G = None, None
    item_here = "No items here"
    holding_anything = None

    main()

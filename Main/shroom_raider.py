#!/usr/bin/env python3
import io
import sys
from argparse import ArgumentParser
from pathlib import Path

from Classes.Entities.Player import Player
from Classes.Grid import Grid

# ! the 2 lines of code below were written with AI assistance
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="ignore")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="ignore")


ENABLE_TEST_MODE = False  # toggle if you want to get logs; for testing
LEVEL_NAME = "TEST"


def check_win_condition(player: Player, grid: Grid) -> None:
    """Check if a player has met the win condition of a grid.

    Args:
        player: A Player Entity
        grid: A Grid object

    """
    if player.get_mushroom_count() == grid.get_total_mushrooms():
        grid.level_clear()


def reset(level: str) -> None:
    """Reset a stage to its starting conditions.

    Args:
        level: A string representation of the stage being reset

    Returns:
        A Grid object that contains the reset level, and a Player entity on that Grid

    """
    main_grid = Grid("test", level)
    main_player = main_grid.get_player()
    return main_grid, main_player


def parser(instructions: str, player: Player, grid: Grid, level: str, reset_only: bool = False) -> None:
    """Parse user inputs to play game.

    Args:
        instructions: The given input string of the player's moves.
        player: The current Player entity.
        grid: The current Grid object.
        level: A string representation of the ORIGINAL stage.
        reset_only: A boolean indicating if moves other than reset can be played.

    """
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
        for inst_raw in line:
            inst = inst_raw.lower()

            if ENABLE_TEST_MODE and inst == "?":
                with open(OUTPUT_LOG_FILE, "w", encoding="utf-8") as f:
                    f.write("CLEAR\n" if grid.get_is_cleared() else "NO CLEAR\n")
                    f.write(grid.get_vis_map_as_str())
                sys.exit()

            if inst == "!":
                grid, player = reset(level)

            if reset_only:
                break

            if grid.get_is_cleared() or player.get_is_dead():
                break

            if inst not in "wasdp!":
                break

            if inst in "wasd":
                player.set_pos(inst)
            elif inst == "p" and player.get_item() is None:
                player.collect_item()

            player.collect_shroom()  # if applicable

            check_win_condition(player, grid)


def main() -> None:
    main_player, main_grid = None, None

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

        main_grid = Grid(LEVEL_NAME, level)
        main_player = main_grid.get_player()

        check_win_condition(main_player, main_grid)

        while True:
            stop_or_reset_only = main_grid.render(main_player, test_mode=ENABLE_TEST_MODE)
            if stop_or_reset_only:
                sys.exit()
            # each input() returns one line; parser will process that line
            parser(input(), main_player, main_grid, level, reset_only=stop_or_reset_only)

    elif args.stage_file is not None:
        with open(args.stage_file, encoding="utf-8") as lvl_file:
            first_line = lvl_file.readline().lstrip("\ufeff")
            r, c = map(int, first_line.split())
            level = lvl_file.read()

        main_grid = Grid("UserInput", level)
        main_player = main_grid.get_player()

        check_win_condition(main_player, main_grid)

        if args.movement_file is None or args.output_file is None:
            while True:
                stop_or_reset_only = main_grid.render(main_player, test_mode=ENABLE_TEST_MODE)
                if stop_or_reset_only:
                    sys.exit()
                parser(input(), main_player, main_grid, level, reset_only=stop_or_reset_only)

        elif args.movement_file is not None and args.output_file is not None:
            parser(args.movement_file, main_player, main_grid, level, reset_only=False)

            with open(args.output_file, "w", encoding="utf-8") as f:
                f.write(f"{r} {c}\n")
                if main_player.get_mushroom_count() == main_grid.get_total_mushrooms():
                    f.write("CLEAR\n")
                else:
                    f.write("NO CLEAR\n")
                f.write(main_grid.get_vis_map_as_str())

        else:  # this is just for safety
            print(
                "Invalid arguments. Usage:\n"
                "python3 shroom_raider.py -f <stage_file>\n"
                "python3 shroom_raider.py -f <stage_file> -m <moves> -o <output_file>",
            )
    else:
        print("Invalid arguments. Use -f <stage_file> or -f <stage_file> -m <moves> -o <output_file>")


if __name__ == "__main__":
    if ENABLE_TEST_MODE:
        base_folder = "Logs"
        Path(base_folder).mkdir(exist_ok=True, parents=True)

        existing = [d for d in Path.iterdir(base_folder) if Path(base_folder, d).is_dir() and d.isdigit()]
        run_number = max([int(d) for d in existing], default=0) + 1

        run_folder = Path(base_folder, str(run_number))
        Path(run_folder).mkdir(parents=True)

        with Path(f"{LEVEL_NAME}.txt").read_text(encoding="utf-8") as src:
            Path(Path(run_folder, "maplayer.txt")).write_text(src.read(), encoding="utf-8")

        INPUT_LOG_FILE = Path(run_folder, "input.txt")
        OUTPUT_LOG_FILE = Path(run_folder, "output.txt")

    main()

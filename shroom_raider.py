#!/usr/bin/env python3
import sys
import io
import os

# ! the 2 lines of code below were written with AI assistance
# ! Prompt: {diogn insert it here} 
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="ignore")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="ignore")

from Classes.Grid import Grid
from Classes.Entities.Player import Player

ENABLE_TEST_MODE = False  # toggle if you want to get logs; for testing
LEVEL_NAME = 'TEST'


def check_win_condition(P, G):
    if P.get_mushroom_count() == G.get_total_mushrooms():
        G.level_clear()


def reset(level):
    global G, P
    G = Grid("test", level)
    P = G.get_player()
    return G, P


def parser(instructions, P: Player, G: Grid, level, reset_only):
    """
    Process instructions. instructions can be:
      - a single-line string ("WASD")
      - a multi-line string ("WAD!WWW\nASDW")
      - an iterable/list of lines (["WAD!WWW", "ASDW"])

    Behavior:
      - Each line is treated like one input() call (interactive).
      - For each line: process characters left-to-right.
      - If a character is invalid (not one of w,a,s,d,p or '!'), stop processing the rest of the current line.
      - If '!' is encountered: reset the level immediately and stop processing the rest of the current line.
      - After finishing a line (or breaking out), continue to the next line (if any).
      - reset_only: if 'reset_only' is passed, parser should stop processing further instructions (keeps previous behavior).
    """
    global item_here, holding_anything

    if instructions is None:
        return

    if isinstance(instructions, str):
        lines = instructions.splitlines() if '\n' in instructions else [instructions]
    else:
        lines = list(instructions)

    if ENABLE_TEST_MODE:
        with open(INPUT_LOG_FILE, "a", encoding="utf-8") as f:
            for ln in lines:
                if ln != '?':
                    f.write(str(ln) + "\n")

    for line in lines:
        for inst in line:
            inst = inst.lower()

            if ENABLE_TEST_MODE and inst == '?':
                with open(OUTPUT_LOG_FILE, "w", encoding="utf-8") as f:
                    f.write("CLEAR\n" if G.get_is_cleared() else "NO CLEAR\n")
                    f.write(G.get_vis_map_as_str())
                exit()

            if inst == '!':
                G, P = reset(level)
                break

            if reset_only:
                break

            if G.get_is_cleared() or P.get_is_dead():
                break

            if inst not in 'wasdp':
                break

            if inst in 'wasd':
                P.set_pos(inst)
            elif inst == 'p':
                if P.get_item() is None:
                    P.collect_item()

            if P.get_item():
                holding_anything = f'Holding item {P.get_item().__class__.__name__}'
            else:
                holding_anything = None

            if P.get_above_item():
                item_here = f'Above item {P.get_above_item()}'
            else:
                item_here = 'No items here'

            if shroom := P.get_above_mushroom():
                shroom.collect(P)

            if P.get_above_water():
                P.destroy()
                P.kill()

            check_win_condition(P, G)

def main():
    global G, P

    args = sys.argv[1:]

    if not args:
        with open(f"{LEVEL_NAME}.txt", encoding="utf-8") as lvl_file:
            first_line = lvl_file.readline().lstrip('\ufeff')
            r, c = map(int, first_line.split())
            level = lvl_file.read()

        G = Grid(LEVEL_NAME, level)
        P = G.get_player()

        check_win_condition(P, G)

        while True:
            stop_or_reset_only = G.render(P, G, item_here, holding_anything, test_mode=ENABLE_TEST_MODE)
            # each input() returns one line; parser will process that line
            parser(input(), P, G, level, stop_or_reset_only)
        return

    # file-based modes (non-interactive)
    if args[0] == "-f" and len(args) >= 2:
        stage_file = args[1]

        with open(stage_file, encoding="utf-8") as lvl_file:
            first_line = lvl_file.readline().lstrip('\ufeff')
            r, c = map(int, first_line.split())
            level = lvl_file.read()

        G = Grid(stage_file, level)
        P = G.get_player()

        check_win_condition(P, G)

        # possible input 1: -f <stage_file> (interactive manual mode)
        if len(args) == 2:
            while True:
                stop_or_reset_only = G.render(P, G, item_here, holding_anything, test_mode=ENABLE_TEST_MODE)
                parser(input(), P, G, level, stop_or_reset_only)

        # possible input 2: -f <stage_file> -m <string_of_moves> -o <output_file>
        # but process the moves with "input #1 semantics" (line-by-line), then emit final output once.
        elif len(args) >= 6 and args[2] == "-m" and args[4] == "-o":
            moves = args[3]    # may contain '\n' to indicate multiple input() lines (for testing), but the CS11 tester will probably not integrate this (we will be working under that assumption)
            out_file = args[5]

            parser(moves, P, G, level, reset_only=False)

            with open(out_file, "w", encoding="utf-8") as f:
                if P.get_mushroom_count() == G.get_total_mushrooms():
                    f.write("CLEAR\n")
                else:
                    f.write("NO CLEAR\n")
                f.write(G.get_vis_map_as_str())

        else: # this is just for safety
            print("Invalid arguments. Usage:\n"
                  "python3 shroom_raider.py -f <stage_file>\n"
                  "python3 shroom_raider.py -f <stage_file> -m <moves> -o <output_file>")
    else:
        print("Invalid arguments. Use -f <stage_file> or -f <stage_file> -m <moves> -o <output_file>")


if __name__ == '__main__':
    P, G = None, None
    item_here = 'No items here'
    holding_anything = None

    if ENABLE_TEST_MODE:
        base_folder = "Logs"
        os.makedirs(base_folder, exist_ok=True)

        existing = [d for d in os.listdir(base_folder) if os.path.isdir(os.path.join(base_folder, d)) and d.isdigit()]
        run_number = max([int(d) for d in existing], default=0) + 1

        run_folder = os.path.join(base_folder, str(run_number))
        os.makedirs(run_folder)

        with open(f'{LEVEL_NAME}.txt', encoding="utf-8") as src, open(os.path.join(run_folder, "map.txt"), "w", encoding="utf-8") as dst:
            dst.write(src.read())

        INPUT_LOG_FILE = os.path.join(run_folder, "input.txt")
        OUTPUT_LOG_FILE = os.path.join(run_folder, "output.txt")

    main()

#!/usr/bin/env python3
import sys
import io
import os

# ! the 2 lines of code below were written with AI assistance
# ! Prompt: {My Python script keeps breaking when I print emojis through subprocess 
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="ignore")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="ignore")

from Classes.Grid import Grid
from Classes.Entities.Player import Player

ENABLE_TEST_MODE = False  # toggle if you want to get logs; for testing
LEVEL_NAME = 'TEST'
REPORT_FILE = None
moves_made = 0


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
    global item_here, holding_anything, moves_made

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

            if reset_only:
                break

            if inst not in 'wasdp!':
                break

            if inst in 'wasd':
                moved = P.set_pos(inst)
                if moved:
                    moves_made += 1
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

            # If the action just cleared the level or killed the player, allow
            # the movement/collection to complete, then stop processing the
            # remainder of the current line.
            if G.get_is_cleared() or P.get_is_dead():
                break


def _maybe_write_report(G, P, win: bool, dead: bool):
    """If REPORT_FILE is set, write a small JSON summary including mushrooms
    collected and moves made so the launcher can update PlayerData.
    """
    import json
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
        # write atomically: write to temp then replace
        tmp = REPORT_FILE + '.tmp'
        with open(tmp, 'w', encoding='utf-8') as f:
            json.dump(payload, f)
            f.flush(); os.fsync(f.fileno())
        try:
            os.replace(tmp, REPORT_FILE)
        except Exception:
            # best effort: try simple write
            with open(REPORT_FILE, 'w', encoding='utf-8') as f:
                json.dump(payload, f)
    except Exception as e:
        print(f"Failed to write report file {REPORT_FILE}: {e}")

def main():
    global G, P, REPORT_FILE, moves_made

    args = sys.argv[1:]

    # support optional report file argument: -R <path>
    if '-R' in args:
        idx = args.index('-R')
        if idx + 1 < len(args):
            REPORT_FILE = args[idx + 1]
            # remove the -R and its value from args so rest of logic is unchanged
            args = args[:idx] + args[idx+2:]

    if not args:
        with open(f"{LEVEL_NAME}.txt", encoding="utf-8") as lvl_file:
            first_line = lvl_file.readline().lstrip('\ufeff')
            r, c = map(int, first_line.split())
            level = lvl_file.read()

        G = Grid(LEVEL_NAME, level)
        P = G.get_player()

        check_win_condition(P, G)

        # initial render before any input so the player sees the starting map
        stop_or_reset_only = G.render(P, G, item_here, holding_anything, test_mode=ENABLE_TEST_MODE)
        while True:
            # each input() returns one line; parser will process that line
            parser(input(), P, G, level, stop_or_reset_only)
            # render once after processing the input so the player sees the
            # resulting map state (single draw per turn). Capture the next
            # stop_or_reset_only for the following loop.
            try:
                stop_or_reset_only = G.render(P, G, item_here, holding_anything, test_mode=ENABLE_TEST_MODE)
            except Exception:
                # best effort: continue even if render fails
                stop_or_reset_only = False
            # after processing a line, if the player cleared or died, exit with code
            if G.get_is_cleared():
                print("CLEAR")
                _maybe_write_report(G, P, True, False)
                sys.exit(0)
            if P.get_is_dead():
                print("DEAD")
                _maybe_write_report(G, P, False, True)
                sys.exit(2)
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
            # initial render once before interactive input loop
            stop_or_reset_only = G.render(P, G, item_here, holding_anything, test_mode=ENABLE_TEST_MODE)
            while True:
                parser(input(), P, G, level, stop_or_reset_only)
                try:
                    stop_or_reset_only = G.render(P, G, item_here, holding_anything, test_mode=ENABLE_TEST_MODE)
                except Exception:
                    stop_or_reset_only = False
                if G.get_is_cleared():
                    print("CLEAR")
                    _maybe_write_report(G, P, True, False)
                    sys.exit(0)
                if P.get_is_dead():
                    print("DEAD")
                    _maybe_write_report(G, P, False, True)
                    sys.exit(2)

        # possible input 2: -f <stage_file> -m <string_of_moves> -o <output_file>
        # but process the moves with "input #1 semantics" (line-by-line), then emit final output once.
        elif len(args) >= 6 and args[2] == "-m" and args[4] == "-o":
            moves = args[3]    # may contain '\n' to indicate multiple input() lines (for testing), but the CS11 tester will probably not integrate this (we will be working under that assumption)
            out_file = args[5]

            parser(moves, P, G, level, reset_only=False)

            # render final frame after applying all moves so output reflects
            # the last state before writing the report/output
            try:
                G.render(P, G, item_here, holding_anything, test_mode=ENABLE_TEST_MODE)
            except Exception:
                pass

            with open(out_file, "w", encoding="utf-8") as f:
                f.write(f'{r} {c}\n')
                if P.get_mushroom_count() == G.get_total_mushrooms():
                    f.write("CLEAR\n")
                    _maybe_write_report(G, P, True, False)
                    sys.exit(0)
                else:
                    f.write("NO CLEAR\n")
                    _maybe_write_report(G, P, False, True)
                    sys.exit(2)

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

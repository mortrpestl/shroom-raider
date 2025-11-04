import sys, io, os, json, time

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

def reset(level):
    global G, P
    G = Grid("test", level)
    P = G.get_player()
    return G, P

def parser(instructions, P: Player, G: Grid, level, reset_only):
    global moves_made
    if instructions is None:
        return
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
                exit()

            # non-WASDP inputs
            if inst == "q":
                print("Quitting to main menu...", flush=True)
                time.sleep(1.5)  # wait 1-2 seconds
                exit(3)
            if inst == "!":
                G, P = reset(level)
            if reset_only:
                break
            if inst not in "wasdp!":
                break
            
            # WASDP inputs
            if inst in "wasd":
                moved = P.set_pos(inst)
                if moved:
                    moves_made += 1
            elif inst == "p":
                if P.get_item() is None:
                    P.collect_item()

            #item collection logic
            if P.get_item(): holding_anything = f"Holding item {P.get_item().__class__.__name__}"
            else: holding_anything = None

            if P.get_above_item(): item_here = f"Above item {P.get_above_item()}"
            else: item_here = "No items here"
            
            #mushroom collection logic
            if shroom := P.get_above_mushroom():
                shroom.collect(P)

            #water destruction logic
            if P.get_above_water():
                P.destroy()
                P.kill()

            #win-loss check
            check_win_condition(P, G)
            if G.get_is_cleared() or P.get_is_dead():
                break

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

def main():
    global G, P, REPORT_FILE, moves_made

    args = sys.argv[1:]
    if "-R" in args:
        idx = args.index("-R")
        if idx + 1 < len(args):
            REPORT_FILE = args[idx+1]
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
        stop_or_reset_only = G.render(P, G, "No items here", None, test_mode=ENABLE_TEST_MODE)
        while True:
            parser(input(), P, G, level, stop_or_reset_only)
            try:
                stop_or_reset_only = G.render(P, G, "No items here", None, test_mode=ENABLE_TEST_MODE)
            except Exception:
                stop_or_reset_only = False
            if G.get_is_cleared():
                print("CLEAR")
                write_report(G, P, True, False)
                sys.exit(0)
            if P.get_is_dead():
                print("DEAD")
                write_report(G, P, False, True)
                sys.exit(2)
        return

    # file-based
    if args[0] == "-f" and len(args) >= 2:
        stage_file = args[1]
        with open(stage_file, encoding="utf-8") as lvl_file:
            first_line = lvl_file.readline().lstrip("\ufeff")
            r,c = map(int, first_line.split())
            level = lvl_file.read()
        G = Grid(stage_file, level)
        P = G.get_player()
        check_win_condition(P, G)

        # possible input 1: -f <stage_file> (interactive manual mode)
        if len(args) == 2:
            stop_or_reset_only = G.render(P, G, "No items here", None, test_mode=ENABLE_TEST_MODE)
            while True:
                parser(input(), P, G, level, stop_or_reset_only)
                try:
                    stop_or_reset_only = G.render(P, G, "No items here", None, test_mode=ENABLE_TEST_MODE)
                except Exception:
                    stop_or_reset_only = False
                if G.get_is_cleared():
                    print("VICTORY")
                    write_report(G, P, True, False)
                    sys.exit(0)
                if P.get_is_dead():
                    print("DEFEAT")
                    write_report(G, P, False, True)
                    sys.exit(2)

        # possible input 2: -f <stage_file> -m <string_of_moves> -o <output_file>
        # but process the moves with "input #1 semantics" (line-by-line), then emit final output once.
        elif len(args) >= 6 and args[2] == "-m" and args[4] == "-o":
            moves = args[3] # may contain '\n' to indicate multiple input() lines (for testing), but the CS11 tester will probably not integrate this (we will be working under that assumption)
            out_file = args[5]
            parser(moves, P, G, level, reset_only=False)
            try:
                G.render(P, G, "No items here", None, test_mode=ENABLE_TEST_MODE)
            except Exception:
                pass
            with open(out_file,"w",encoding="utf-8") as f:
                f.write(f"{r} {c}\n")
                if P.get_mushroom_count() == G.get_total_mushrooms():
                    f.write("CLEAR\n")
                    write_report(G, P, True, False)
                    sys.exit(0)
                else:
                    f.write("NO CLEAR\n")
                    write_report(G, P, False, True)
                    sys.exit(2)
        else:
            print("Invalid arguments. Usage:\npython3 shroom_raider.py -f <stage_file>\npython3 shroom_raider.py -f <stage_file> -m <moves> -o <output_file>")
    else:
        print("Invalid arguments. Use -f <stage_file> or -f <stage_file> -m <moves> -o <output_file>")

if __name__ == "__main__":
    P,G = None,None
    if ENABLE_TEST_MODE:
        # test-mode logging setup (unchanged)
        os.makedirs("Logs",exist_ok=True)
    main()

import sys
import os

from Classes.Grid import Grid
from Classes.Entities.Player import Player

item_here = 'No items here'
holding_anything = None

ENABLE_TEST_MODE = True #toggle if you want to get logs; for testing
LEVEL_NAME = 'test1'

def check_win_condition(P,G):
    if P.get_mushroom_count() == G.get_total_mushrooms():
        G.level_clear()

# for generating test
if ENABLE_TEST_MODE:
    base_folder = "Logs"
    os.makedirs(base_folder, exist_ok=True)
    
    existing = [d for d in os.listdir(base_folder) if os.path.isdir(os.path.join(base_folder, d)) and d.isdigit()]
    run_number = max([int(d) for d in existing], default=0) + 1
    
    run_folder = os.path.join(base_folder, str(run_number))
    os.makedirs(run_folder)
    
    with open(f'Levels/{LEVEL_NAME}.txt', encoding="utf-8") as src, open(os.path.join(run_folder, "map.txt"), "w", encoding="utf-8") as dst:
        dst.write(src.read())

    INPUT_LOG_FILE = os.path.join(run_folder, "input.txt")
    OUTPUT_LOG_FILE = os.path.join(run_folder, "output.txt")

def reset(level):
    global G, P
    G = Grid("test", level)
    P = G.get_player()
    return G,P

def parser(instructions, P: Player, G, level, reset_only):
    global item_here, holding_anything

    if ENABLE_TEST_MODE:
        with open(INPUT_LOG_FILE, "a", encoding="utf-8") as f:
            if instructions!='?': f.write("".join(instructions)+"\n")

    for inst in instructions:
        inst = inst.lower()

        if ENABLE_TEST_MODE and inst == '?':
            with open(OUTPUT_LOG_FILE, "w", encoding="utf-8") as f:
                if G.get_is_cleared():
                    f.write("CLEAR\n")
                else:
                    f.write("NO CLEAR\n")
                f.write(G.get_vis_map_as_str())
            exit()
        
        if inst == '!':
            G, P = reset(level)
        if reset_only == 'reset_only':
            continue
    
        if G.get_is_cleared() or P.get_is_dead():
            continue

        
        
        elif inst in 'wasd':
            P.set_pos(inst)
        elif inst == 'p':
            if P.get_item() is None:
                P.collect_item()
        else:
            break

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

        check_win_condition(P,G)


def main():
    global G, P

    args = sys.argv[1:]

    if not args:
        #no arguments: manual play using default LEVEL_NAME
        with open(f"Levels/{LEVEL_NAME}.txt", encoding="utf-8") as lvl_file:
            r, c = map(int, lvl_file.readline().split())
            level = lvl_file.read()

            G = Grid(LEVEL_NAME, level)
            P = G.get_player()
            print()

            check_win_condition(P,G)

            while (stop_or_reset_only := G.render(P, G, item_here, holding_anything, test_mode=ENABLE_TEST_MODE)) != "stop":
                parser(input(), P, G, level, stop_or_reset_only)
        return

    if args[0] == "-f" and len(args) >= 2:
        stage_file = args[1]

        with open(stage_file, encoding="utf-8") as lvl_file:
            r, c = map(int, lvl_file.readline().split())
            level = lvl_file.read()

        G = Grid(stage_file, level)
        P = G.get_player()
        
        check_win_condition(P,G)
        
        #possible input 1: -f <stage_file>
        if len(args) == 2:
            while (stop_or_reset_only := G.render(P, G, item_here, holding_anything, test_mode=ENABLE_TEST_MODE)) != "stop":
                parser(input(), P, G, level, stop_or_reset_only)

        #possible input 2: -f <stage_file> -m <string_of_moves> -o <output_file>
        elif len(args) >= 6 and args[2] == "-m" and args[4] == "-o":
            moves = args[3]
            out_file = args[5]

            for m in moves:
                parser(m, P, G, level, reset_only=False)

            with open(out_file, "w", encoding="utf-8") as f:
                if P.get_mushroom_count() == G.get_total_mushrooms():
                    f.write("CLEAR\n")
                else:
                    f.write("NO CLEAR\n")
                f.write(G.get_vis_map_as_str())

        else:
            print("Invalid arguments. Usage:\n"
                  "python3 shroom_raider.py -f <stage_file>\n"
                  "python3 shroom_raider.py -f <stage_file> -m <moves> -o <output_file>")
    else:
        print("Invalid arguments. Use -f <stage_file> or -f <stage_file> -m <moves> -o <output_file>")
     
if __name__ == '__main__':
    P, G = None, None
    main()

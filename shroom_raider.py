import sys

from Classes.Grid import Grid
from Classes.Entities.Player import Player

item_here = 'No items here'
holding_anything = None
mushrooms_collected = 0

def reset(level):
    global G, P
    G = Grid("test", level)
    P = G.get_player()
    return G,P

def parser(instructions,p:Player,g,level,reset_only):
    global item_here, holding_anything, mushrooms_collected
    for inst in instructions:
        inst = inst.lower()
        if inst=='!':
            g,p = reset(level)
        if reset_only=='reset_only':
            continue
        elif inst in 'wasd':
            p.set_pos(inst)
        elif inst=='p':
            if p.get_item() == None: #! TEST: Will item in inventory be replaced if picked up new item?
                p.collect_item()
        else:
            continue

        if p.get_item(): 
            holding_anything = f'Holding item {p.get_item().__class__.__name__}'
        else:
            holding_anything = None

        if p.get_above_item(): 
            item_here = f'Above item {p.get_above_item()}'
        else:
            item_here = 'No items here'

        if shroom:=p.get_above_mushroom():
            shroom.collect(p)

        if p.get_above_water():
            p.destroy()
            p.kill()
            return g, None

def main():
    global G, P

    if len(sys.argv) == 1: 
        # * This is where we will have our main menu
        # ! Code below is for testing

        with open("Levels/test.txt", encoding="utf-8") as lvl_file:
            r, c = lvl_file.readline().split()
            level = lvl_file.read()

            G = Grid("test", level)
            

            P = G.get_player()
            print()

            while (stop_or_reset_only:=G.render(P,G,item_here,holding_anything))!="stop":
                parser(input(),P,G,level,stop_or_reset_only)

        
    # ! TODO: Should probably refactor the code below        
    elif len(sys.argv) == 2: 
        with open(sys.argv[1], encoding='utf-8') as lvl_file:
            r, c = lvl_file.readline().split()
            level = lvl_file.read()

            G = Grid('Level X', level)
            G.render()

            P = G.get_player()

            while True:
                G, P = parser(input('Type input here: '), P, G, level)
        ...
    elif len(sys.argv) == 3:
        with open(sys.argv[1], encoding='utf-8') as lvl_file:
            with open(sys.argv[2], encoding='utf-8') as inpt_file:

                            r, c = lvl_file.readline().split()
            level = lvl_file.read()

            G = Grid('Level X', level)
            G.render()

            P = G.get_player()

            inputs = inpt_file.readline()
            while True:
                G, P = parser(inputs, P, G, level)
                
    else:
        print('Invalid Arguments')
    
if __name__ == '__main__':
    P, G = None, None
    main()

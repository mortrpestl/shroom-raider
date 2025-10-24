import sys

from Classes.Grid import Grid
from Classes.Entities.Player import Player

def reset(level):
    global G, P
    G = Grid("test", level)
    P = G.get_player()
    return G,P

def item_equipped(p):
    return p.get_item()

def parser(instructions,p,g,level):
    for inst in instructions:
        inst = inst.lower()
        if inst=='!':
            g,p = reset(level)
        elif inst in 'wasdWASD':
            p.set_pos(inst)
        elif inst=='pP':
            p.collect_item()
        else:
            pass
        g.render()
        if item_equipped(p): print(f'Item equipped: {item_equipped(p).__class__.__name__}')
        if p.above_item(): 
            print(f'You are above item "{p.above_item()}". Collect with "p"?')
        if  shroom:=p.above_mushroom(): 
            shroom.collect(p)

            print(f'Collected a mushroom! You now have {p.get_mushroom_count()} mushroom{"s" if p.get_mushroom_count()>1 else ""}.')

    return g,p


def main():
    global G, P

    if len(sys.argv) == 1: 
        # * This is where we will have our main menu
        # ! Code below is for testing

        with open("Levels/test10.txt", encoding="utf-8") as lvl_file:
            r, c = lvl_file.readline().split()
            level = lvl_file.read()

            G = Grid("test", level)
            
            G.render()

            P = G.get_player()

            while True:
                G,P = parser(input('Type input here: '),P,G,level)
                
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

import sys
from argparse import ArgumentParser

from Classes.Grid import Grid
from Classes.Entities.Player import Player

def reset(level):
    global g
    g = Grid("test", level)
    p = g.get_player()
    return g,p

def item_equipped(p):
    return p.get_item()

def parser(instructions,p,g,level):
    for inst in instructions:
        inst = inst.lower()
        if inst=='!':
            g,p = reset(level)
        elif inst in 'wasd':
            p.set_pos(inst)
        elif inst=='p':
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
    if len(sys.argv) == 1: 
        # * This is where we will have our main menu
        # ! Code below is for testing

        with open("Levels/test10.txt", encoding="utf-8") as lvl_file:
            r, c = lvl_file.readline().split()
            level = lvl_file.read()
            print(level)

            g = Grid("test", level)
            
            g.render()

            p = g.get_player()

            while True:
                g,p = parser(input('Type input here: '),p,g,level)
                
    elif len(sys.argv) == 2: 
        # * If given level file, but no instructions file
        ...
    elif len(sys.argv) == 3:
        # * If given level file and instructions file 
        ...
    else:
        print('Invalid Arguments')
    

main()

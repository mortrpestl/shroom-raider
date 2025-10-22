import sys
from argparse import ArgumentParser

from Classes.Grid import Grid
from Classes.Entities.Player import Player


def main():
    if len(sys.argv) == 1: 
        # * This is where we will have our main menu
        # ! Code below is for testing

        with open("Levels/test.txt", encoding="utf-8") as lvl_file:
            r, c = lvl_file.readline().split()
            level = lvl_file.read()
            print(level)

            g = Grid("test", level)
            g.render()

            p = g.get_player()

            while True:
                p.set_pos(input('hello: '))
                g.render()
                print(p.get_pos())
                
    elif len(sys.argv) == 2: 
        # * If given level file, but no instructions file
        ...
    elif len(sys.argv) == 3:
        # * If given level file and instructions file 
        ...
    else:
        print('Invalid Arguments')
    

main()

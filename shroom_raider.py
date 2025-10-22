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

            g = Grid("test", level)
            g.render()

            p = g.get_player()

            while True: # ! refactor to add an endgame condition
                player_input = input('Direction?: ')

                if len(player_input) == 0:
                    continue
                elif len(player_input) == 1:
                    p.set_pos(player_input)
                else:
                    for i in player_input:
                        p.set_pos(i)

                g.render()
                
    elif len(sys.argv) == 2: 
        # * If given level file, but no instructions file
        ...
    elif len(sys.argv) == 3:
        # * If given level file and instructions file 
        ...
    else:
        print('Invalid Arguments')
    

main()

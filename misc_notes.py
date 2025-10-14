"""
ITEMS:
L🧑 - Laro Craft
.   - empty tile
T🌲 - tree
+🍄 - mushroom
R🪨 - rock
~🟦 - water
-⬜ - paved tile

x🪓 - axe
*🔥 - flamethrower

STAGE FILE:
r c 
<r lines>

CONTROLS:
WASD / ULDR - movement (case insensitive)
P           - pick up item on current tile
!           - reset the stage
string of moves allowed
all other characters are invalid

GAMEPLAY LOOP:
UI representation
Mushrooms collected so far
Item currently holding (if any)
Item on tile currently at (if any)
Prompt for user input

END STATE:
if all mushrooms collected/Laro falls into water
show: won/lost / mushrooms collected

BONUS FEATURES:
check file 

POSSIBLY HELPFUL FEATURES:
termcolor
pyxel
pygame
1-second short animations
Note: Do not alter tiles/items in Features section
"""

#HELPER FEATURES
import os

def clear():
    """
    Clears terminal for new game output.
    """
    os.system('cls' if os.name=='nt' else 'clear')

import random
n=42
for _ in range(n):
    print(random.randint(1,10))



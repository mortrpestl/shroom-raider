from random import randint, choice
from map_gen import *

empty_tile = '.'
tiles = 'T'
pushables = '#Ro'
deadly_tiles = '~&'
items = '!x*'

elements = get_items_and_probabilities(allowed_to_spawn=tiles+pushables+items, probabilities_shown=False)

def map_surround(parse, inner_rads, outer_rads, elements_to_surround = elements):

    elements_to_surround = prob_list_from_dict(elements_to_surround)

    if isinstance(inner_rads, int): inner_rads = (inner_rads,inner_rads)
    if isinstance(outer_rads, int): outer_rads = (outer_rads,outer_rads)

    inner_lower_bound, inner_upper_bound = inner_rads
    outer_lower_bound, outer_upper_bound = outer_rads
    inner_rad_range = range(inner_lower_bound, inner_upper_bound+1)
    outer_rad_range = range(outer_lower_bound, outer_upper_bound+1)

    parse = parse.strip().split('\n')

    R,C,grid = 0,0,0
    R,C = map(int,parse[0].split())

    grid = [list(r) for r in parse[1:]]
    player_pos = []

    for r in range(R):
        for c in range(C):
            if grid[r][c]=='L': player_pos.append((r,c))

    if not player_pos: raise ValueError('Player not found')

    def manhattan(r1,r2,c1,c2):
        return abs(r1-r2)+abs(c1-c2)
    
    for pr,pc in player_pos:
        rand_inner_rad = choice(inner_rad_range)
        rand_outer_rad = choice(outer_rad_range)
        for r in range(R):
            for c in range(C):
                if rand_inner_rad <= manhattan(r,pr,c,pc) <= rand_outer_rad:
                    grid[r][c] = choice(elements_to_surround)
        grid[pr][pc] = '.'

    if place_player: place_player(R,C,grid)

    return f"{R} {C}\n" + "\n".join("".join(r) for r in grid)



#example 1: surround laro with Radius

element_probi_quarry = {'R':50,'T':5, 'o':5, '#':5}

empty_map = gen_map(20,20,{'.':1},player_exists = False)

print(empty_map)
exit()

new_map = place_laro_center(gen_map(29,29,{'.':1},player_exists = False))

existing_map = """
29 29
...~..oooooRRRRoRRRRRoo......
.+...ooRRRRRoooRoRRRoRoo...+.
.._.oRRRRoRRooRRRRRoRoRRR....
~..RRRRoRRoRRooRRRoRRRoRoR.~.
..RoRooooRRoRoooooooooRRoRo..
.oRoRRRoRooRRRooRoRRooRoooRo.
oRooRooRooRRRRRRRRoRoRoooRRoR
oooooRoRoRoRoRoooooRRoooRoRRo
RoRRRRooooRooRooRRoRRRoRRoRRR
RoRRRooRRoooRR.RRoRoRoRRoRRRo
RoRoRooRRooRo...RRooooRRoRRRo
RooRRRoRRoRo.T..!ooooRooRoRRR
RooooRoRoRo!.TT..!oRRRoRRRRoR
RRRoRooooR!..TxTTT.RRoRoRooRo
RRoRooooR...TxLxT...oooRoRRRR
oRoRooRoRR.TTTxT_.!RoRoRooooR
oRRoRoRRRoo...TT.!oRRRRRRRoRo
oRooooRooooo!..T.oRoooRRooRoo
oooRoRooRoRoR!..oRooooRRRRoRR
oRooRoRRRRoRoo.oRRooRoRRRoRoo
oooRRRoRooooooRooRRRoRooRRooo
RRRRRRooRoRoRooooRoRoooRoRooo
oRoRRRRooRRoRooRoRRoRoRRooooo
.oRRoRRRoRRRoRRRRoRRRoooRoRo.
..ooooRoooRoRRRRRoRRRRRooRR..
...oRoooooRoRRoRoooRoRoooR..~
~...RoRRRRRRoRRoRRoRRRRRR....
.+...RoRRoooRoRRooRRRoRo...+.
..._..RRoooRRoRoooRRooR......
"""

surround_laro = map_surround(existing_map, 6,22,element_probi_quarry)
print(surround_laro)

#example 2: randomize map
exit()
R,C = 100,200
parse = gen_map_with_seeds(100,200, seeds=80)

grid_diag = (R*C) // (R+C)
inner_rad = (5,10)
outer_rad = (10,15)

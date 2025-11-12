from random import randint, choice
from map_tools import get_items_and_probabilities, gen_map, gen_map_with_seeds, place_player

empty_tile = '.'
tiles = 'T'
pushables = '#Ro'
deadly_tiles = '~&'
items = '!x*'

elements = get_items_and_probabilities(allowed_to_spawn=tiles+pushables+items, probabilities_shown=False)

def map_surround(parse, inner_rads, outer_rads, elements_to_surround = elements):

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
            if grid[r][c]=='X': player_pos.append((r,c))

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

    place_player(R,C,grid)

    return f"{R} {C}\n" + "\n".join("".join(r) for r in grid)

R,C = 100,200
parse = gen_map_with_seeds(100,200, seeds=80)

grid_diag = (R*C) // (R+C)
inner_rad = (5,10)
outer_rad = (10,15)


print(map_surround(parse, inner_rad, outer_rad))
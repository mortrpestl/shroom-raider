import random
from random import randint, choice

empty_tile = '.'
tiles = 'T'
pushables = '#Ro'
deadly_tiles = '~&'
items = '!x*'

neutral = empty_tile+tiles+pushables
harmful = deadly_tiles
helpful = items

#base element probi
element_probi = {
    empty_tile: 100,
    tiles + deadly_tiles: 2,
    pushables: 1,
    items: 3,
}

def place_player(R,C,map,offset_from_edge = 0):
    map[randint(0+offset_from_edge, R-1-offset_from_edge)][randint(0+offset_from_edge, C-1-offset_from_edge)] = "L"

# * Probability Determiner Helper Functions
def get_indiv_probi():

    indiv_element_probi = {}

    for key, prob in element_probi.items():
        for char in key: indiv_element_probi[char] = prob

    return indiv_element_probi

def get_items_and_probabilities(allowed_to_spawn = None, probabilities_shown = True):
    """
    Provide a string that will only let the ASCII given in the string appear in the generated map
    """
    element_prob = get_indiv_probi()

    if not allowed_to_spawn: 
        if probabilities_shown:
            return element_prob
        else: 
            return ''.join(element_prob.keys())

    if allowed_to_spawn:
        if probabilities_shown:
            return {k:v for k,v in element_prob.items() if k in allowed_to_spawn}
        else:
            return ''.join(k for k in element_prob.keys() if k in allowed_to_spawn)

# * Primitive Map Generator Functions
def gen_map(R,C, element_probi = get_indiv_probi()):
    elements = [
        char
        for char, prob in element_probi.items()
        for _ in range(prob)
    ]

    
    map = []
    for r in range(R):
        row = []
        for c in range(C):
            if r in (0, R-1) or c in (0, C-1):
                row.append(".")
            else:
                row.append(elements[randint(0, len(elements)-1)])
        map.append(row)

    place_player(R,C,map,offset_from_edge=1)

    return f"{R} {C}\n" + "\n".join("".join(row) for row in map)

def generate_n_maps(lowest_R, lowest_C, n=10, start_numbering=1, highest_R=None, highest_C=None):
    """
    Example usage:
    lowest_R, highest_R = (30, 30)
    lowest_C, highest_C = (30, 30)
    generate_n_maps(
        lowest_R=lowest_R, lowest_C=lowest_C, highest_R=highest_R, highest_C=highest_C
    )
    """

    if highest_R is None and highest_C is None:
        highest_R = lowest_R
        highest_C = lowest_C
    maps = []

    for i in range(n):
        R, C = random.randint(lowest_R, highest_R), random.randint(lowest_C, highest_C)

        map = gen_map(R, C)
        filename = f"Levels/test{start_numbering + i}.txt"
        with open(filename, "w") as f:
            f.write(map)
        maps.append(map)

    return "".join(maps)

# * Miscellaneous Map Generators

# * Primitive Map Generator Functions
def gen_map_with_seeds(R,C,seeds=5):
    """
    Randomly places 'X's in a map to seed for better map generation.
    """

    new_map = [list(r) for r in gen_map(R,C).split('\n')[1:]]

    for i in range(seeds):
        random_R = randint(0,R-1)
        random_C = randint(0,C-1)

        new_map[random_R][random_C] = 'X'

    return f"{R} {C}\n" + "\n".join("".join(row) for row in new_map)
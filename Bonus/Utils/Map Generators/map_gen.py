import math
import pathlib
import random
from random import choice, randint

empty_tile = "."
tiles = "T_"
pushables = "#Ro"
deadly_tiles = "~&"
items = "!x*?"
mushroom = "+"
player = "L"

neutral = empty_tile + tiles + pushables
harmful = deadly_tiles
helpful = items

ALL = neutral + harmful + helpful + mushroom + player

# base element probi
element_probi = {
    empty_tile: 100,
    tiles + deadly_tiles: 20,
    pushables: 10,
    items: 0,
}

# * Helper Functions


def replace_empty_tiles_with_random(input_map, element_probi=None, replace_chars=None):
    if element_probi is None:
        element_probi = get_indiv_probi()

    if replace_chars is None:
        replace_chars = "._"

    elements = prob_list_from_dict(element_probi)
    header, grid, R, C = parse_map(input_map)

    for r in range(R):
        for c in range(C):
            if grid[r][c] in replace_chars:
                grid[r][c] = random.choice(elements)

    return build_map(header, grid)


def parse_map(input_map):
    input_map = input_map.split("\n")
    header = input_map[0]
    R, C = map(int, header.split())
    grid = [list(r) for r in input_map[1:]]
    return header, grid, R, C


def build_map(header, grid):
    return header + "\n" + stringify(grid)


def stringify(grid):
    return "\n".join("".join(g) for g in grid)


def prob_list_from_dict(element_probi):
    lst = []
    for char, prob in element_probi.items():
        lst.extend([char] * prob)
    return lst


def place_player(R, C, map, offset_from_edge=0):
    map[randint(0 + offset_from_edge, R - 1 - offset_from_edge)][
        randint(0 + offset_from_edge, C - 1 - offset_from_edge)
    ] = "L"


# * Probability Determiner Helper Functions
def get_indiv_probi(element_probi=element_probi):

    indiv_element_probi = {}

    for key, prob in element_probi.items():
        for char in key:
            indiv_element_probi[char] = prob

    return indiv_element_probi


def get_items_and_probabilities(allowed_to_spawn=None, probabilities_shown=True):
    """Provide a string that will only let the ASCII given in the string appear in the generated map"""
    element_prob = get_indiv_probi()

    if not allowed_to_spawn:
        if probabilities_shown:
            return element_prob
        else:
            return "".join(element_prob.keys())

    if allowed_to_spawn:
        if probabilities_shown:
            return {k: v for k, v in element_prob.items() if k in allowed_to_spawn}
        else:
            return "".join(k for k in element_prob.keys() if k in allowed_to_spawn)


# * Primitive Map Generator Functions
def gen_map(R, C, element_probi=None, player_exists=True, boost_prob=None):
    if element_probi is None:
        element_probi = get_indiv_probi()

    if boost_prob:
        element_probi = element_probi.copy()
        for char, mult in boost_prob:
            if char in element_probi:
                element_probi[char] = int(element_probi[char] * mult)

    elements = [char for char, prob in element_probi.items() for _ in range(prob)]
    grid = [[random.choice(elements) for c in range(C)] for r in range(R)]

    if player_exists:
        place_player(R, C, grid, offset_from_edge=1)

    return build_map(f"{R} {C}", grid)


def gen_empty_map(R, C, element_probi={".": 50, "_": 1}):
    return gen_map(R, C, element_probi)


def generate_n_maps(lowest_R, lowest_C, n=10, start_numbering=1, highest_R=None, highest_C=None):
    """Example usage:
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
        pathlib.Path(filename).write_text(map)
        maps.append(map)

    return "".join(maps)


# * Miscellaneous Map Generators


# * Primitive Map Generator Functions
def gen_map_with_seeds(R, C, seeds=5):
    """Randomly places 'X's in a map to seed for better map generation."""
    new_map = [list(r) for r in gen_map(R, C).split("\n")[1:]]

    for i in range(seeds):
        random_R = randint(0, R - 1)
        random_C = randint(0, C - 1)

        new_map[random_R][random_C] = "X"

    return f"{R} {C}\n" + "\n".join("".join(row) for row in new_map)


def place_laro_center(input_map):
    header, grid, R, C = parse_map(input_map)
    grid[R // 2][C // 2] = "L"
    return build_map(header, grid)


# * Painting Utilities


def draw_circles(input_map, centers=None, char="R", fill=False, fatness=0.4, use_numbered_cells=False, mult=1):
    header, grid, R, C = parse_map(input_map)

    if use_numbered_cells:
        centers = []
        for r in range(R):
            for c in range(C):
                if grid[r][c].isdigit():
                    radius = int(grid[r][c])
                    centers.append((r, c, radius))
                    grid[r][c] = char

    if not centers:
        return build_map(header, grid)

    for r in range(R):
        for c in range(C):
            for cx, cy, radius in centers:
                radius = radius * mult
                dist = math.sqrt((r - cx) ** 2 + (c - cy) ** 2)
                if (fill and dist <= radius) or (not fill and abs(dist - radius) < fatness):
                    grid[r][c] = char

    return build_map(header, grid)


def draw_lines(
    input_map,
    line_mode="row",
    points=None,
    element_probi=None,
    thickness=1,
    use_X_coords=False,
    canyonize=True,
):

    header, grid, R, C = parse_map(input_map)

    if element_probi is None:
        element_probi = get_indiv_probi()
    elements = prob_list_from_dict(element_probi)

    if use_X_coords:
        points = [(r, c) for r in range(R) for c in range(C) if grid[r][c] == "X"]
        if not points:
            return input_map

    if line_mode == "row":
        points.sort(key=lambda x: (x[0], x[1]))
    if line_mode == "column":
        points.sort(key=lambda x: (x[1], x[0]))

    # Bresenham interpolation hehe
    def draw_segment(r1, c1, r2, c2):
        steps = round(max(abs(r2 - r1), abs(c2 - c1)))
        for i in range(steps + 1):  # include endpoint
            t = i / steps if steps else 0
            r = int(r1 + (r2 - r1) * t) + (choice(range(-1, 1)) if canyonize else 0)
            c = int(c1 + (c2 - c1) * t) + (choice(range(-1, 1)) if canyonize else 0)
            # add thickness
            for dr in range(-thickness, thickness + 1):
                for dc in range(-thickness, thickness + 1):
                    rr, cc = r + dr, c + dc
                    if 0 <= rr < R and 0 <= cc < C and math.sqrt(dr**2 + dc**2) <= thickness:
                        grid[rr][cc] = choice(elements)

    if line_mode in ("row", "column"):
        for i in range(len(points) - 1):
            draw_segment(*points[i], *points[i + 1])
    else:
        edges_drawn = set()
        for p1 in points:
            nearest = None
            min_dist = float("inf")
            for p2 in points:
                if p1 == p2:
                    continue
                if (p1, p2) in edges_drawn or (p2, p1) in edges_drawn:
                    continue
                dist = (p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2
                if dist < min_dist:
                    min_dist = dist
                    nearest = p2
            if nearest:
                draw_segment(*p1, *nearest)
                edges_drawn.add((p1, nearest))

    return build_map(header, grid)


# sidenote: compprog techniques in map generation is kinda crazy LOL
def draw_polygon_hull(input_map, points, polygon_char="R", thickness=1, canyonize=True):
    if not points:
        return input_map

    header, grid, R, C = parse_map(input_map)

    def cross(o, a, b):
        return (a[1] - o[1]) * (b[0] - o[0]) - (a[0] - o[0]) * (b[1] - o[1])

    points = sorted(set(points))
    if len(points) == 1:
        hull = points
    else:
        # lower hull
        lower = []
        for p in points:
            while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
                lower.pop()
            lower.append(p)
        # upper hull
        upper = []
        for p in reversed(points):
            while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
                upper.pop()
            upper.append(p)
        hull = lower[:-1] + upper[:-1]

    # Bresenham interpolation hehe
    def draw_segment(r1, c1, r2, c2):
        steps = round(max(abs(r2 - r1), abs(c2 - c1)))
        for i in range(steps + 1):
            t = i / steps if steps else 0
            r = int(r1 + (r2 - r1) * t) + (choice(range(-1, 1)) if canyonize else 0)
            c = int(c1 + (c2 - c1) * t) + (choice(range(-1, 1)) if canyonize else 0)
            for dr in range(-thickness, thickness + 1):
                for dc in range(-thickness, thickness + 1):
                    rr, cc = r + dr, c + dc
                    if 0 <= rr < R and 0 <= cc < C and math.sqrt(dr**2 + dc**2) <= thickness:
                        grid[rr][cc] = polygon_char

    for i in range(len(hull)):
        draw_segment(*hull[i], *hull[(i + 1) % len(hull)])

    return build_map(header, grid)


# * EXAMPLE USAGE

print(gen_empty_map(50, 50, element_probi={"~": 50}))
randR, randC = randint(3, 30), randint(3, 30)

# 0. Generate empty map
# print(gen_empty_map(15,30))

# 1. Generate map with boosted probabilities for tree

# element_probi = {'T':1, '.':2}
# print(gen_map(10,20, element_probi=element_probi))

# 2. Draw circles on coordinates
# print(draw_circles(gen_empty_map(20,25),[(4,4,5),(20,20,7)], fatness=0.7))

# 3. Draw filled circles in coordinates
# print(draw_circles(gen_empty_map(25,25),[(2,2,2),(20,20,5),(3,18,4),(10,10,7),(22,5,2),(10,23,5),(16,-3,4)], char='T', fatness=2))

# print(draw_circles(gen_empty_map(25,25),[(-3,-3,20)],fatness=3))

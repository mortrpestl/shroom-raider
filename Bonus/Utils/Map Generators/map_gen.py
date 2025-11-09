import random

element_probabilities = {
    ".": 100,
    "T": 10,
    "R": 10,
    "x": 10,
    "*": 10,
    "_": 10,
    "~": 10,
    "+": 10,
}

elements = [
    tile
    for (element, prob) in element_probabilities.items()
    for generated_tiles in list(prob * element)
    for tile in generated_tiles
]


def map_gen(R, C):
    map = []
    for r in range(R):
        row = []
        for c in range(C):
            if r in (0, R - 1) or c in (0, C - 1):
                row.append("T")
            else:
                row.append(elements[random.randint(0, len(elements) - 1)])
        map.append(row)

    map[random.randint(1, R - 2)][random.randint(1, C - 2)] = "L"

    return "\n".join("".join(row) for row in map)


def generate_n_maps(
    lowest_R, lowest_C, n=10, start_numbering=1, highest_R=None, highest_C=None
):
    if highest_R is None and highest_C is None:
        highest_R = lowest_R
        highest_C = lowest_C
    maps = []

    for i in range(n):
        R, C = random.randint(lowest_R, highest_R), random.randint(lowest_C, highest_C)

        map = f"{R} {C}\n{map_gen(R, C)}"
        filename = f"Levels/test{start_numbering + i}.txt"
        with open(filename, "w") as f:
            f.write(map)

        maps.append(map)

    return "".join(maps)


# generate_n_maps(10, 8, 10, 13, 20, 1)
lowest_R, highest_R = (30, 30)
lowest_C, highest_C = (30, 30)
generate_n_maps(
    lowest_R=lowest_R, lowest_C=lowest_C, highest_R=highest_R, highest_C=highest_C
)

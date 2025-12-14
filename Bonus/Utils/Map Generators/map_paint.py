from map_gen import *


def paint(
    input_map,
    line_char="#",
    polygon_char="R",
    line_thickness=1,
    circle_char="T",
    fill_circles=False,
    fatness=0.4,
    canyonize=True,
    mult=1,
):
    header, grid, R, C = parse_map(input_map)

    # extract points
    X_points = [(r, c) for r in range(R) for c in range(C) if grid[r][c] == "X"]
    P_points = [(r, c) for r in range(R) for c in range(C) if grid[r][c] == "P"]
    circle_centers = []
    for r in range(R):
        for c in range(C):
            if grid[r][c].isdigit():
                circle_centers.append((r, c, int(grid[r][c])))
                grid[r][c] = "."  # temporarily clear

    clean_map = build_map(header, grid)

    # draw X lines
    clean_map = draw_lines(
        clean_map,
        points=X_points,
        element_probi={line_char: 1},
        thickness=line_thickness,
        canyonize=canyonize,
    )

    # draw P polygon
    clean_map = draw_polygon_hull(
        clean_map,
        P_points,
        polygon_char=polygon_char,
        thickness=line_thickness,
        canyonize=canyonize,
    )

    # draw circles
    clean_map = draw_circles(
        clean_map,
        centers=circle_centers,
        char=circle_char,
        fill=fill_circles,
        fatness=fatness,
        mult=mult,
    )

    return clean_map


# MAP = gen_map(50, 50, element_probi={".": 1})
# MAP = place_laro_center(MAP)
# print(MAP)


MAP = """25 25
RRRRRRRRRRRRRRRRRRRRRRRRR
RRRRRRRRRRRRRRRRRRRRRRRRR
RRRRRRRRRRRRRRRRRRRRRRRRR
RRRRRRRRRRRRRRRRRRRRRRRRR
RRRRRRRRRRRRRRRRRRRRRRRRR
RRRRRRRRRRRRRRRRRRRRRRRRR
RRRRRRRRRRRRRRRRRRRRRRRRR
RRRRRRRRRRRRRRRRRRRRRRRRR
RRRRRRRRRRRRRRRRRRRRRRRRR
RRRRRRRRRRRRRRRRRRRRRRRRR
RRRRRRRRRRRRRRRRRRRRRRRRR
RRRRRRRRRRRRRRRRRRRRRRRRR
RRRRRRRRRRRR9RRRRRRRRRRRR
RRRRRRRRRRRRRRRRRRRRRRRRR
RRRRRRRRRRRRRRRRRRRRRRRRR
RRRRRRRRRRRRRRRRRRRRRRRRR
RRRRRRRRRRRRRRRRRRRRRRRRR
RRRRRRRRRRRRRRRRRRRRRRRRR
RRRRRRRRRRRRRRRRRRRRRRRRR
RRRRRRRRRRRRRRRRRRRRRRRRR
RRRRRRRRRRRRRRRRRRRRRRRRR
RRRRRRRRRRRRRRRRRRRRRRRRR
RRRRRRRRRRRRRRRRRRRRRRRRR
RRRRRRRRRRRRRRRRRRRRRRRRR
RRRRRRRRRRRRRRRRRRRRRRRRR"""

# example 1:
painted_map = paint(
    MAP,
    polygon_char="o",
    circle_char=".",
    line_char="T",
    line_thickness=0.8,
    canyonize=0,
    fatness=0.8,
    fill_circles=False,
    mult=1.2,
)

print(place_laro_center(painted_map))

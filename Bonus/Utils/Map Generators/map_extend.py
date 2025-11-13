def extend(where: str, amt: int, text: str) -> str:
    lines = text.split("\n")
    width = len(lines[0]) if lines else 0

    if where == "a":  # left
        lines = ["." * amt + line for line in lines]
    elif where == "d":  # right
        lines = [line + "." * amt for line in lines]

    width = len(lines[0]) if lines else 0

    if where == "w":  # up
        lines = ["." * width] * amt + lines
    elif where == "s":  # down
        lines = lines + ["." * width] * amt

    return "\n".join(lines)


to_process = """8 30
...........RRRRRRR............
......._..RRRRRRRRR...........
......_.RRRRR...RRRRR.........
.......RRRR.....L.RRRR........
.....RRRRR.........RRRR.......
....RRRR.............RRR......
...RRRR...............RX......
..RRR........_................
"""

lines = to_process.strip().split("\n")
R, C = map(int, lines[0].split())
grid = "\n".join(lines[1:])

directions = {
    "w": 0,
    "a": 0,
    "s": 0,
    "d": 20,
}

for dir_, amt in directions.items():
    grid = extend(dir_, amt, grid)

grid = grid.split("\n")
print(len(grid), len(grid[0]))
print(*grid, sep="\n")

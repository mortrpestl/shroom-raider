from map_gen import *

def trimmer(input_map):
    rows = []
    for i in input_map.split('\n'):
        rows.append(i.strip())
    return '\n'.join(rows)

def check_validity(input_map):
    try:
        header, grid, R, C = parse_map(input_map)
        
        rowlog = []
        messages = []
        mistake_found = False
        
        if len(grid)!=R: 
            messages.append(f'wrong row size: {R}=/=correct:{len(grid)}')
            mistake_found = True
        if len(grid[0])!=C: 
            messages.append(f'wrong column size: {C}=/=correct:{len(grid[0])}')
            mistake_found = True
        
        laro_found = 0 

        for r in range(len(grid)):
            rowlog.append(f"at row {r}, {''.join(grid[r])}, length {len(grid[r])}")

            for c in range(len(grid[0])):
                if grid[r][c] not in ALL: 
                    messages.append(f'character "{grid[r][c]}" for at row {r}, column {c}')
                    grid[r][c] = '💔'
                    mistake_found = True
                if grid[r][c] == 'L': laro_found += 1
        
        if laro_found > 1: messages.append(f'Too many Laros: {laro_found}>1'); mistake_found = True
        if laro_found == 0: messages.append(f'No Laros in grid: {laro_found}<1'); mistake_found = True

        if mistake_found: 
            print('\n'.join(rowlog)+'\n')
            print('\n'.join(messages))
        else: print('\nGood to go!\n')

        return trimmer(build_map(header, grid))
    except Exception:
        print(*rowlog, sep='\n')
        print(*messages, sep='\n')
        return 'Mistake(s) found'

MAP = """21 20
+T...............T&L
~T..............T..&
~T.............T..T.
~.._....._.....#.T..
~.............#.....
~............#......
~...........#.......
~..........#........
~.........#.........
~........#..........
~.......#....._.....
~......#....._......
~.....#.............
~....#..............
~...#...............
~..#................
~.#.................
~#..................
#...................
R...................
...................."""

# print(check_validity(trimmer(MAP)))
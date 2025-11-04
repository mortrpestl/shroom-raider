import random

element_probabilities = {
    '.':100,
    'T':0,
    'R':0,
    'x':0,
    '*':0,
    '_':0,
    '~':0,
    '+':0,}

elements = [l for (element, prob) in element_probabilities.items() for a in list(prob*element) for l in a]

def map_gen(R,C):
    map = []
    for r in range(R):
        row = []
        for c in range(C):
            if (r in (0,R-1) or c in (0,C-1)): row.append('.')
            else:
                row.append(elements[random.randint(0,len(elements)-1)])
        map.append(row)

    # map[random.randint(1,R-2)][random.randint(1,C-2)]='L'

    return f'{R} {C}\n' + '\n'.join(''.join(row) for row in map)

print(map_gen(25,25))
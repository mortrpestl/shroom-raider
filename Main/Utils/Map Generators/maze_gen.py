from random import randint

def maze_gen(R,C):
    R,C=2*R+1,2*C+1
    
    grid=[]
    for r in range(R):
        T=[]
        for c in range(C):
            if r in (0,R-1) or c in (0,C-1): T.append('T')
            elif r%2==1 and c%2==1: T.append('.')
            elif r%2==0 and c%2==0: T.append('T')
            else: T.append("T...."[randint(0,4)])
        grid.append(T)

    for r in grid:
        print(''.join(r))

maze_gen(randint(3,10),randint(3,10))

CHARTAPE = r'''0gqbmpWKBfZViX5azxo4RMFs.n}yj1DSAuHrLtdQI3OJk2Cc'9"8TvNU7 ,YP/h{lewE6:G'''
CHARTAPE_LEN = len(CHARTAPE)
VALID_LETTERS = set(CHARTAPE)


def check_validity(data: str):
    if len(data) > 30:
        return False
    
    for letter in data:
        if letter not in VALID_LETTERS:
            return False
    else:
        return True

def shift(letter: str, shiftval: str):
    i = CHARTAPE.index(letter)

    shiftRight = CHARTAPE.index(shiftval)
    i += shiftRight

    return CHARTAPE[i % CHARTAPE_LEN]
    

def unshift(letter: str, shiftval: str):
    i = CHARTAPE.index(letter)
    shiftLeft = CHARTAPE.index(shiftval)

    i -= shiftLeft

    if i < 0:
        i += CHARTAPE_LEN
    
    return CHARTAPE[i % CHARTAPE_LEN]

def scramble(data: str, key: str):
    res = r''

    for i in range(len(data)):
        res += shift(data[i], key[i % len(key)])

    return res

def unscramble(data: str, key: str):
    res = r''

    for i in range(len(data)):
        res += unshift(data[i], key[i % len(key)])
    
    return res

def findPW(unencrypted: str, encrypted: str): # we assume that these are the same len
    pw = r''
    for i in range(len(unencrypted)):
        i1 = CHARTAPE.index(unencrypted[i])
        i2 = CHARTAPE.index(encrypted[i])
        # find the diff between each letter

        shift = 0
        if i2 > i1:
            shift = i2 - i1
        elif i2 < i1:
            shift = (i2 + CHARTAPE_LEN) - i1
        else:
            shift = 0

        pw += CHARTAPE[shift]

    return pw


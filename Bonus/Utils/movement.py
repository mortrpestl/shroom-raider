from keyboard import is_pressed as p
from keyboard import block_key as b

ACTIVE = False

def block_keys():
    for _ in range(1, 84):
        b(_)

def check_movement():
    global ACTIVE

    keys = (p('w'), p('s'), p('a'), p('d'), p('p'), p('f'), p('shift+!'), p('shift+q'))

    keys_pressed = keys.count(True)

    if keys_pressed == 1:
        if not ACTIVE:
            ACTIVE = True
            if keys[0]: return 'w'
            elif keys[1]: return 's'
            elif keys[2]: return 'a'
            elif keys[3]: return 'd'
            elif keys[4]: return 'p'
            elif keys[5]: return 'f'
            elif keys[6]: return '!'
            else: return 'Q'

    elif keys_pressed == 0:
        ACTIVE = False
        return None
    else:
        return None
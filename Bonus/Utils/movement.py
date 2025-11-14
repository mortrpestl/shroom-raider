from keyboard import block_key as b
from keyboard import is_pressed as p
from keyboard import unblock_key as ub
from Utils.sounds import menu_sound

ACTIVE = False


def block_keys():
    for _ in range(1, 84):
        b(_)


def unblock_keys():
    for _ in range(1, 84):
        ub(_)


def check_movement():
    global ACTIVE

    keys = (p("w"), p("s"), p("a"), p("d"), p("p"), p("f"), p("shift+!"), p("shift+q"))

    keys_pressed = keys.count(True)

    if keys_pressed == 1:
        if not ACTIVE:
            ACTIVE = True
            if keys[0]:
                return "w"
            elif keys[1]:
                return "s"
            elif keys[2]:
                return "a"
            elif keys[3]:
                return "d"
            elif keys[4]:
                return "p"
            elif keys[5]:
                return "f"
            elif keys[6]:
                return "!"
            else:
                return "Q"

    elif keys_pressed == 0:
        ACTIVE = False
        return None
    else:
        return None


def menu_movement():  # yes, this doesn't follow the DRY principle, but it makes the code more performant in menus since it counts less things per tick
    global ACTIVE

    keys = (p("w"), p("s"), p("enter"), p("shift+!"), p("shift+q"))

    keys_pressed = keys.count(True)

    if keys_pressed == 1:
        if not ACTIVE:
            menu_sound()
            ACTIVE = True
            if keys[0]:
                return "w"
            elif keys[1]:
                return "s"
            elif keys[2]:
                return "enter"
            elif keys[3]:
                return "!"
            else:
                return "Q"

    elif keys_pressed == 0:
        ACTIVE = False
        return None
    else:
        return None

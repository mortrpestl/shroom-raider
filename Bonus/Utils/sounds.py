from pygame import mixer as m
from random import randint

# ! REGULAR GAME

# ? Movement Sounds
WALK = []
PAVEDWALK = []
ONITEM = None
PUSH = []
FAILPUSH = None
DEATH = None

# ? Item Sounds
AXE, FLAMETHROWER, SHROOM = None, None, None
EQUIP = None

# ! BONUS

# ? Added Map Entities
ICE = None
LOG = None
BEE = None
BEE_DEATH = None

# ? Added Items
BOMB = None
FLASH = None

# ? Menu Sounds
MENU = None


# ! Helper Functions
def path(filename: str):
    return "Assets/Sounds/" + filename

# ! Initializers
def initialize_walk_sounds():
    global WALK, PAVEDWALK, PUSH, FAILPUSH, ONITEM, DEATH
    walk_filenames = [
        "emptytile_step1.mp3",
        "emptytile_step2.mp3",
        "emptytile_step3.mp3",
        "emptytile_step4.mp3",
        "emptytile_step5.mp3",
        "emptytile_step6.mp3",
    ]
    paved_walk_filenames = [
        "pavedtile_step1.mp3",
        "pavedtile_step2.mp3",
        "pavedtile_step3.mp3",
    ]
    push_filenames = ["push1.mp3", "push2.mp3"]

    for a in walk_filenames:
        WALK.append(m.Sound(path(a)))

    for a in paved_walk_filenames:
        PAVEDWALK.append(m.Sound(path(a)))

    for p in push_filenames:
            PUSH.append(m.Sound(path(p)))

    ONITEM = m.Sound(path("on_item.ogg"))

    FAILPUSH = m.Sound(path("push_not_successful.mp3"))
    DEATH = m.Sound(path("death.ogg"))


def initialize_item_usages():
    global AXE, FLAMETHROWER, SHROOM, FLASH, EQUIP

    EQUIP = m.Sound(path("equip.ogg"))
    AXE = m.Sound(path("axe_tree.mp3"))
    FLAMETHROWER = m.Sound(path("burn_tree.ogg"))
    SHROOM = m.Sound(path("mushroom_collected.mp3"))
    FLASH = m.Sound(path("flash.ogg"))


def initialize_bonus():
    global ICE, LOG, BOMB, BEE, BEE_DEATH
    ICE = m.Sound(path("ice.ogg"))
    LOG = m.Sound(path("move_log.ogg"))
    BOMB = m.Sound(path("bomb.ogg"))
    BEE = m.Sound(path("bee_move.ogg"))
    BEE_DEATH = m.Sound(path("bee_death.ogg"))


def initialize_menu():
    global MENU
    MENU = m.Sound(path("main_menu_click.ogg"))


def initAll():
    m.init()
    initialize_walk_sounds()
    initialize_bonus()
    initialize_item_usages()
    initialize_menu()


# ! Sound Players
def walk_sound():
    global WALK
    i = randint(0, len(WALK) - 1)

    WALK[i].play()


def paved_walk():
    global PAVEDWALK
    i = randint(0, len(PAVEDWALK) - 1)

    PAVEDWALK[i].play()


def on_item_sound():
    global ONITEM
    if ONITEM:
        ONITEM.play()


# the following code was made using AI:
# prompt: make me functions to play all the rest of the sounds that I defined above. if there are multiple variants, then use the format I showed in walk_sound(), else, just play the sound from the global variable


def axe_sound():
    global AXE
    if AXE:
        AXE.play()


def flamethrower_sound():
    global FLAMETHROWER
    if FLAMETHROWER:
        FLAMETHROWER.play()


def shroom_sound():
    global SHROOM
    if SHROOM:
        SHROOM.play()


def flash_sound():
    global FLASH
    if FLASH:
        FLASH.play()


def push_sound():
    global PUSH
    if not PUSH:
        return
    i = randint(0, len(PUSH) - 1)
    PUSH[i].play()


def failpush_sound():
    global FAILPUSH
    if FAILPUSH:
        FAILPUSH.play()


def death_sound():
    global DEATH
    if DEATH:
        DEATH.play()


def equip_sound():
    global EQUIP
    if EQUIP:
        EQUIP.play()


# bonus


def ice_sound():
    global ICE
    if ICE:
        ICE.play()


def log_sound():
    global LOG
    if LOG:
        LOG.play()


def bomb_sound():
    global BOMB
    if BOMB:
        BOMB.play()


def bee_sound():
    global BEE
    if BEE:
        BEE.play()


def bee_death_sound():
    global BEE_DEATH
    if BEE_DEATH:
        BEE_DEATH.play()


# menu
def menu_sound():
    global MENU
    if MENU:
        MENU.play()

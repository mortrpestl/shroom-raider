from random import randint

from pygame import mixer as m

import os
from LevelManager import get_folder_bgm_filename

HERE = os.path.dirname(__file__)

def path(filename: str):
    return os.path.join(HERE, "Assets", "Sounds", filename)

# ! REGULAR GAME

# ? Movement Sounds
WALK = []
PAVEDWALK = []
ONITEM = None
PUSH = []
FAILPUSH = None
WATER = None

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

# ? Background Music
FADE_MS = 1000
BGM = None
WELCOME_BGM = None

# ? Level End Sounds
VICTORY = None
DEFEAT = None

# ! Helper Functions
def path(filename: str):
    return "Assets/Sounds/" + filename


# ! Initializers
def initialize_walk_sounds():
    global WALK, PAVEDWALK, PUSH, FAILPUSH, ONITEM, WATER
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
    WATER = m.Sound(path("death.ogg"))


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

def initialize_bgms():
    global BGM, WELCOME_BGM
    BGM = m.Sound(path("bgm.mp3"))
    WELCOME_BGM = m.Sound(path("welcome_bgm.mp3"))

def initialize_victory_defeat():
    global VICTORY, DEFEAT
    VICTORY = m.Sound(path("victory_sound.mp3"))
    DEFEAT = m.Sound(path("defeat_sound.mp3"))


def initAll():
    m.init()
    initialize_walk_sounds()
    initialize_bonus()
    initialize_item_usages()
    initialize_menu()
    initialize_bgms()
    initialize_victory_defeat()


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


def water_sound():
    global WATER
    if WATER:
        WATER.play()


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

# * Victory and Defeat

def victory_sound():
    global VICTORY
    if VICTORY:
        VICTORY.play()

def defeat_sound():
    global DEFEAT
    if DEFEAT:
        DEFEAT.play()

# * BGM

def current_bgm_stop():
    global BGM, FADE_MS
    BGM.fadeout(FADE_MS)

# welcome bgm
def welcome_sound():
    global WELCOME_BGM
    if WELCOME_BGM:
        WELCOME_BGM.play(loops=-1, fade_ms=FADE_MS)


def welcome_sound_stop():
    global WELCOME_BGM
    WELCOME_BGM.fadeout(FADE_MS)


# mainmenubgm
def mainmenu_sound():
    current_bgm_stop()
    global BGM
    BGM = m.Sound(path("bgm.mp3"))
    if BGM:
        BGM.play(loops=-1, fade_ms=FADE_MS)


# level bgm
def level_bgm_sound(level_bgm):
    current_bgm_stop()
    global BGM, FADE_MS
    try:
        bgm_file = path(os.path.join("level_music", level_bgm))
        BGM = m.Sound(bgm_file)
        BGM.play(loops=-1, fade_ms=FADE_MS)
    except Exception:
        print(f"failed to play level BGM <{bgm_file}>")

# folder bgm
def folder_bgm_sound(folder_id):
    current_bgm_stop()
    global BGM, FADE_MS

    try:
        folder_bgm = get_folder_bgm_filename(folder_id)
        bgm_file = path(os.path.join("folder_music", folder_bgm))

        BGM = m.Sound(bgm_file)
        BGM.play(loops=-1, fade_ms=FADE_MS)

    except Exception:
        print(f"failed to play folder BGM <{bgm_file}>")
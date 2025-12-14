import os
import pathlib
from random import randint

from LevelManager import get_folder_bgm_filename
from pygame import mixer as m

HERE = os.path.dirname(__file__)


def path(filename: str):
    return os.path.join(HERE, "..", "Assets", "Sounds", filename)


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
QUIT_FADE_MS = 2000

BGM = None
WELCOME_BGM = None

# ? Level End Sounds
VICTORY = None
DEFEAT = None

# ! Helper Functions
# --- SOUND CACHE + PRELOADS ---
SOUND_CACHE = {}
PRELOADED_LEVEL_BGM = {}
PRELOADED_FOLDER_BGM = {}
PRELOADED_MAINMENU_BGM = None


def load_sound(fullpath: str):
    fp = os.path.normpath(fullpath)
    if not pathlib.Path(fp).is_absolute():
        fp = os.path.normpath(os.path.join(HERE, fp))
    if fp in SOUND_CACHE:
        return SOUND_CACHE[fp]
    snd = m.Sound(fp)
    SOUND_CACHE[fp] = snd
    return snd


def preload_level_bgms():
    level_dir = os.path.join(HERE, "..", "Assets", "Sounds", "level_music")
    if not pathlib.Path(level_dir).is_dir():
        return
    for fn in os.listdir(level_dir):
        if not fn.lower().endswith((".mp3", ".ogg", ".wav")):
            continue
        full = os.path.join(level_dir, fn)
        snd = load_sound(full)
        PRELOADED_LEVEL_BGM[fn] = snd


def preload_folder_bgms():
    folder_dir = os.path.join(HERE, "..", "Assets", "Sounds", "folder_music")
    if not pathlib.Path(folder_dir).is_dir():
        return
    for fn in os.listdir(folder_dir):
        if not fn.lower().endswith((".mp3", ".ogg", ".wav")):
            continue
        full = os.path.join(folder_dir, fn)
        snd = load_sound(full)
        PRELOADED_FOLDER_BGM[fn] = snd


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
        WALK.append(load_sound(path(a)))

    for a in paved_walk_filenames:
        PAVEDWALK.append(load_sound(path(a)))

    for p in push_filenames:
        PUSH.append(load_sound(path(p)))

    ONITEM = load_sound(path("on_item.ogg"))

    FAILPUSH = load_sound(path("push_not_successful.mp3"))
    WATER = load_sound(path("death.ogg"))


def initialize_item_usages():
    global AXE, FLAMETHROWER, SHROOM, FLASH, EQUIP

    EQUIP = load_sound(path("equip.ogg"))
    AXE = load_sound(path("axe_tree.mp3"))
    FLAMETHROWER = load_sound(path("burn_tree.ogg"))
    SHROOM = load_sound(path("mushroom_collected.mp3"))
    FLASH = load_sound(path("flash.ogg"))


def initialize_bonus():
    global ICE, LOG, BOMB, BEE, BEE_DEATH
    ICE = load_sound(path("ice.ogg"))
    LOG = load_sound(path("move_log.ogg"))
    BOMB = load_sound(path("bomb.ogg"))
    BEE = load_sound(path("bee_move.ogg"))
    BEE_DEATH = load_sound(path("bee_death.ogg"))


def initialize_menu():
    global MENU
    MENU = load_sound(path("main_menu_click.ogg"))


def initialize_bgms():
    global BGM, WELCOME_BGM, PRELOADED_MAINMENU_BGM
    PRELOADED_MAINMENU_BGM = load_sound(path("bgm.mp3"))
    WELCOME_BGM = load_sound(path("welcome_bgm.mp3"))


def initialize_victory_defeat():
    global VICTORY, DEFEAT
    VICTORY = load_sound(path("victory_sound.mp3"))
    DEFEAT = load_sound(path("defeat_sound.mp3"))


def initAll():
    m.init()
    preload_level_bgms()
    preload_folder_bgms()
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
    current_bgm_stop()
    if VICTORY:
        VICTORY.play()


def defeat_sound():
    global DEFEAT
    current_bgm_stop()
    if DEFEAT:
        DEFEAT.play()


# * BGM
# stop current BGM
def current_bgm_stop(fade_ms=FADE_MS):
    if BGM:
        BGM.fadeout(fade_ms)


# welcome BGM
def welcome_sound(fade_ms=FADE_MS):
    if WELCOME_BGM:
        WELCOME_BGM.play(loops=-1, fade_ms=fade_ms)


def welcome_sound_stop(fade_ms=FADE_MS):
    if WELCOME_BGM:
        WELCOME_BGM.fadeout(fade_ms)


# main menu BGM
def mainmenu_sound(fade_ms=FADE_MS):
    current_bgm_stop(fade_ms)
    global BGM
    BGM = PRELOADED_MAINMENU_BGM
    if BGM:
        BGM.play(loops=-1, fade_ms=fade_ms)


# level BGM
def level_bgm_sound(level_bgm, fade_ms=FADE_MS):
    current_bgm_stop(fade_ms)
    global BGM
    BGM = PRELOADED_LEVEL_BGM.get(level_bgm)
    if BGM:
        BGM.play(loops=-1, fade_ms=fade_ms)


# folder BGM
def folder_bgm_sound(folder_id, fade_ms=FADE_MS):
    current_bgm_stop(fade_ms)
    global BGM
    folder_bgm = get_folder_bgm_filename(folder_id)
    BGM = PRELOADED_FOLDER_BGM.get(folder_bgm)
    if BGM:
        BGM.play(loops=-1, fade_ms=fade_ms)


def fadeout_all_sounds(fade_ms=FADE_MS):
    for sound in [BGM, WELCOME_BGM]:
        if sound:
            sound.fadeout(fade_ms)

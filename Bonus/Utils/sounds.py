from pygame import mixer as m
from random import randint
from time import sleep

WALK = []
PAVEDWALK = []
AXE, FLAMETHROWER, SHROOM, FLASH = None, None, None, None

PUSH = []
FAILPUSH = None

FAE = None

# used this to save on typing: AI
#for every playsound function, add a small 0.75 second delay to everything

# helper func
def path(filename: str):
    return 'Assets/Sounds/' + filename

def initialize_walk_sounds():
    global WALK, PAVEDWALK
    walk_filenames = ['emptytile_step1.mp3', 'emptytile_step2.mp3', 'emptytile_step3.mp3', 'emptytile_step4.mp3', 'emptytile_step5.mp3', 'emptytile_step6.mp3']
    paved_walk_filenames = ['pavedtile_step1.mp3', 'pavedtile_step2.mp3', 'pavedtile_step3.mp3']
    
    for a in walk_filenames:
        WALK.append(m.Sound(path(a)))

    for a in paved_walk_filenames:
        PAVEDWALK.append(m.Sound(path(a)))

def initialize_item_usages():
    global AXE, FLAMETHROWER, SHROOM, FLASH

    AXE = m.Sound(path('axe_tree.mp3'))
    FLAMETHROWER = m.Sound(path('burn_tree.mp3'))
    SHROOM = m.Sound(path('mushroom_collected.mp3'))
    FLASH = m.Sound(path('use_flash1.mp3'))

def initialize_push_and_fae():
    global PUSH, FAILPUSH, FAE
    push_filenames = ['push1.mp3', 'push2.mp3']

    for p in push_filenames:
        PUSH.append(m.Sound(path(p)))

    FAILPUSH = m.Sound(path('push_not_successful.mp3'))
    FAE = m.Sound(path('fae_circle_enter.mp3'))

def initAll():
    m.init()
    initialize_walk_sounds()
    initialize_push_and_fae()
    initialize_item_usages()


def walk_sound():
    global WALK
    i = randint(0, len(WALK) - 1)

    WALK[i].play()

def paved_walk():
    global PAVEDWALK
    i = randint(0, len(PAVEDWALK) - 1)

    PAVEDWALK[i].play()

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

def fae_sound():
    global FAE
    if FAE:
        FAE.play()


import os
import time
import sys
from emoji import is_emoji


def __clear_terminal():
    os.system("cls" if os.name == "nt" else "clear")


def __wait(seconds):
    time.sleep(seconds)


def load_in(input_str):
    input_str = input_str.split("\n")
    height = len(input_str)
    wave = []
    for i in range(height):
        temp = []
        for j in input_str[i]:
            if j in " 　":
                temp.append(j)
            elif is_emoji(j):
                temp.append("==")
            else:
                temp.append("=")
        wave.append("".join(temp))

    for i in range(height):
        __clear_terminal()
        for j in range(i + 1):
            print(input_str[j])
            sys.stdout.flush()
        k = 0
        for line in range(i, min(height - 1, i + 3)):
            match k:
                case 0:
                    print(wave[line])
                    sys.stdout.flush()
                case 1:
                    print(wave[line].replace("=", "-"))
                    sys.stdout.flush()
                case 2:
                    print(wave[line].replace("=", "."))
                    sys.stdout.flush()
            k += 1
        __wait(0.15)  # delay for animation

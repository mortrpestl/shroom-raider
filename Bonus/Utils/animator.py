import sys
from emoji import is_emoji
from Utils.general_utils import clear_prev_n_lines, center_wr_to_terminal_size, wait
from colorama import Fore, Back, Style


def load_in(input_str, total_time=1.5, centered=True):
    input_str = input_str.split("\n")
    height = len(input_str)
    delta_time = total_time / height

    wave = []
    for i in range(height):
        temp = []
        for j in input_str[i]:
            if j in " 　⠀":
                temp.append(j)
            elif is_emoji(j):
                temp.append("==")
            else:
                temp.append("=")
        wave.append("".join(temp))

    if centered:
        input_str = center_wr_to_terminal_size(input_str).split("\n")
        wave = center_wr_to_terminal_size(wave).split("\n")

    for i in range(height):
        print(input_str[i])
        sys.stdout.flush()
        k = 0
        for line in range(i + 1, min(height - 1, i + 4)):
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
        wait(delta_time)  # delay for animation
        clear_prev_n_lines(k)


def typewriter(input_str, total_time=1.5, centered=True):
    delta_time = total_time / len(input_str)
    input_str = input_str.split("\n")

    if centered:
        input_str = center_wr_to_terminal_size(input_str).split("\n")

    for line in input_str:
        for char in line:
            print(char, end="")
            sys.stdout.flush()
            if char not in " 　⠀":
                wait(delta_time)
            if char in ".,":
                wait(delta_time*1.2)
        print()
        sys.stdout.flush()

def progress_bar(deco_str, total_time = 1.5, centered=True):
    delta_time = total_time / 100

    if centered:
        print(center_wr_to_terminal_size(deco_str, colors=[Fore.RED]))
        sys.stdout.flush()
        for frame in range(1, 101):
            print(center_wr_to_terminal_size((str(frame) + "%") + 
                                             ("▓" * (frame // 5) + "▒░" + " " * (20-frame//5))[:20] +
                                             (" " * len(str(frame)))), end="\r")
            sys.stdout.flush()
            wait(delta_time)

    else:
        print(Fore.RED + deco_str + Style.RESET_ALL)
        sys.stdout.flush()
        for frame in range(1, 101):
            print((str(frame) + "%") + ("▓" * (frame // 5) + "▒░")[:20], end="\r")
            sys.stdout.flush()
            wait(delta_time)
import sys
from emoji import is_emoji
from Utils.general_utils import clear_prev_n_lines, center_wr_to_terminal_size, wait
from colorama import Fore, Back, Style


def load_in(input_str, 
            total_time=1.5, 
            centered=True, 
            colors: list=[], 
            colors2: list=[], 
            fx_map: str="=-.", 
            mode: str="--normal",
            color_grid: list=[[]]
            ):
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
                temp.append(fx_map[0] * 2)
            else:
                temp.append(fx_map[0])
        wave.append("".join(temp))

    if mode == "--normal": # normal mode: one color per line
        if centered:
            input_str = center_wr_to_terminal_size(input_str, colors).split("\n")
            wave = center_wr_to_terminal_size(wave, colors if not colors2 else colors2).split("\n")
        elif colors:
            input_str = colors + input_str + [Style.RESET_ALL]
            wave = (colors if not colors2 else colors2) + wave + [Style.RESET_ALL]

    elif mode == "--alternate": # alternate mode: alternate colors per line
        for i in range(height):
            using_color = colors if i % 2 else colors2
            if centered:
                input_str[i] = center_wr_to_terminal_size(input_str[i], using_color)
                wave[i] = center_wr_to_terminal_size(wave[i], using_color)
            elif colors:
                input_str[i] = "".join(using_color + [input_str[i]] + [Style.RESET_ALL])
                wave[i] = "".join(using_color + [wave[i]] + [Style.RESET_ALL])
            
    
    for i in range(height):
        print(input_str[i])
        sys.stdout.flush()
        k = 0
        for line in range(i + 1, min(height, i + 4)):
            match k:
                case 0:
                    print(wave[line])
                    sys.stdout.flush()
                case 1:
                    print(wave[line].replace(fx_map[0], fx_map[1]))
                    sys.stdout.flush()
                case 2:
                    print(wave[line].replace(fx_map[0], fx_map[2]))
                    sys.stdout.flush()
            k += 1
        wait(delta_time)  # delay for animation
        clear_prev_n_lines(k)


def typewriter(input_str, total_time=1.5, centered=True, colors: list=[]):
    delta_time = total_time / len(input_str)
    input_str = input_str.split("\n")

    if centered:
        input_str = center_wr_to_terminal_size(input_str, colors).split("\n")
    elif colors:
        input_str = colors + input_str + [Style.RESET_ALL]

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
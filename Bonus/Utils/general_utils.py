import time
import os
import sys
from wcwidth import wcswidth
from colorama import Style, Fore, Back

WAIT_TIME = 5
DEBUG_MODE = True


def clear_terminal():
    os.system("cls" if os.name == "nt" else "clear")


def clear_prev_n_lines(n):
    for _ in range(n):
        sys.stdout.write("\033[F")
        sys.stdout.write("\033[K")


def wait(seconds):
    time.sleep(seconds)


def center_wr_to_terminal_size(input_str: str | list[str], colors: list = [], grid_mode=False):
    """Centers strings, optionally with color per line."""
    if isinstance(input_str, str):
        input_str = input_str.split("\n")
    # otherwise, its already a list
    width = os.get_terminal_size()[0]
    result = []

    if not grid_mode:  # center a line, then wrap it with color.
        for line in input_str:
            txt_width = wcswidth(line)
            if txt_width != -1:
                padding_left = (width - txt_width) // 2
                if colors:
                    result.append("".join([" "] * padding_left + colors + [line] + [Style.RESET_ALL]))
                else:
                    result.append("".join([" "] * padding_left + [line]))
            else:
                result.append(line)

    else:  # colors must be a list of lists
        for r in range(len(input_str)):
            txt_width = wcswidth(input_str[r])
            if txt_width == -1:
                result.append(input_str[r])
                continue
            padding_left = (width - txt_width) // 2
            row_result = [" " * padding_left]
            for c in range(len(input_str[0])):
                row_result.append("".join(colors[r][c] + input_str[r][c]))
            result.append("".join(row_result) + Style.RESET_ALL)

    return "\n".join(result)


# decorator
def debug_wait(delay=2.5):
    def decorator(func):
        def wrapper(*args, **kwargs):
            answer = func(*args, **kwargs)
            if DEBUG_MODE:
                print("DEBUG MODE ON. Happy debugging! Turn off by toggling DEBUG_MODE in general_utils")
                wait(delay)
            return answer

        return wrapper

    return decorator


def print_and_wait(message, seconds=1):
    print(message)
    wait(seconds)
    clear_terminal()


def format_time(seconds: float) -> str:
    m, s = divmod(seconds, 60)
    return f"{int(m):02}:{s:06.3f}"


# yes, that's my 10G code right there with some modifications
def tabulate(headers, table, sep=" ", lborder=" ", rborder=" ", tborder="=", joint="+", max_width=20):
    def truncate(text, width):
        text = "" if text is None else str(text)
        # replace NaN with -
        if text.lower() == "nan":
            text = "-"
        return text if len(text) <= width else text[: max(0, width - 3)] + "..."

    table = [headers] + table
    R, C = len(table), len(headers)
    # compute max widths
    col_widths = [min(max(len(truncate(table[r][c], max_width)) for r in range(R)) + 2, max_width) for c in range(C)]

    def build_border():
        return joint + joint.join(tborder * w for w in col_widths) + joint

    def build_row(row):
        cells = [truncate(str(row[c]), col_widths[c]).center(col_widths[c]) for c in range(C)]
        return lborder + sep.join(cells) + rborder

    lines = [build_border(), build_row(headers), build_border()]
    for row in table[1:]:
        lines.append(build_row(row))
    lines.append(build_border())

    # fix intersections
    final_lines = []
    for line in lines:
        if line.startswith(joint):
            currLine = list(line)
            for j in range(1, len(currLine) - 1):
                if (
                    currLine[j] == joint
                    and currLine[j - 1] in {joint, lborder, rborder, sep}
                    and currLine[j + 1] in {joint, lborder, rborder, sep}
                ):
                    currLine[j] = joint  # intersection points
            final_lines.append("".join(currLine))
        else:
            final_lines.append(line)

    return center_wr_to_terminal_size("\n".join(final_lines), colors=[Fore.BLUE])

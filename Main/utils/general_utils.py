import os
import sys
import time
from collections.abc import Callable
from math import ceil
from typing import Concatenate, ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")

WAIT_TIME = 5
DEBUG_MODE = True


def clear_terminal() -> None:
    """Clear the terminal."""
    os.system("cls" if os.name == "nt" else "clear")


def clear_prev_n_lines(n: int) -> None:
    """Clear the previous n lines.

    Args:
        n (int): number of lines to clear.

    """
    for _ in range(n):
        sys.stdout.write("\033[F")
        sys.stdout.write("\033[K")


def wait(seconds: float) -> None:
    """Do nothing for the specified amount of seconds.

    Args:
        seconds (float|int): seconds to wait.

    """
    time.sleep(seconds)


# decorator
def debug_wait(delay: float = 2.5) -> Callable[[Callable[P, R]], Callable[Concatenate[str, P], R]]:
    """Debug decorator factory for functions.

    Args:
        delay (float|int): time to wait.

    Returns:
        The decorated function with debug!

    """

    def decorator(func: Callable[P, R]) -> Callable[Concatenate[str, P]]:
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            answer = func(*args, **kwargs)
            if DEBUG_MODE:
                print("DEBUG MODE ON. Happy debugging! Turn off by toggling DEBUG_MODE in general_utils")
                wait(delay)
            return answer

        return wrapper

    return decorator


def print_and_wait(message: str, seconds: float = 1) -> None:
    """Print a message then wait some number of seconds.

    Args:
        message (str): the message to print.
        seconds (float|int): waiting time after print.

    """
    print(message)
    wait(seconds)
    clear_terminal()


def format_time(seconds: float) -> str:
    """Format time in the hh:mm:ss format.

    Args:
        seconds (float|int): time to format.

    Returns:
        A string of the formatted time.

    """
    m, s = divmod(seconds, 60)
    return f"{int(m):02}:{s:06.3f}"


def calculate_percentage(num: float, den: float) -> str:
    """Calculate formatted percentage (xx%). 0% if divided by 0.

    Args:
        num (float|int): numerator of the fraction.
        den (float|int): denominator of the fraction.

    Returns:
        A string in the format xx%.

    """
    if den == 0:
        return "0%"
    return str(ceil((num / den) * 100)) + "%"


# yes, that's my 10G code right there with some modifications
def tabulate(
    headers: list[str],
    table: list[list],
    sep: str = " ",
    tborder: str = "=",
    joint: str = "+",
) -> str:
    """Generate a table.

    Args:
        headers (list[str]): Headers for the table.
        table (list[list]): List containing rows for the table.
        sep (str): border character between the columns.
        tborder (str): top and bottom border character.
        joint (str): intersection between border elements.

    Returns:
        A multi-line string of the table.

    """
    max_width = 20

    def truncate(text: str, width: int) -> str:
        """Reduce a string to a specified width.

        Args:
            text (str): text to truncate.
            width (int): width to adhere to

        Returns:
            The truncated string.

        """
        text = "" if text is None else str(text)
        # replace NaN with -
        if text.lower() == "nan":
            text = "-"
        return text if len(text) <= width else text[: max(0, width - 3)] + "..."

    table = [headers, *table]
    r, c = len(table), len(headers)
    # compute max widths
    col_widths = [min(max(len(truncate(table[r][c], max_width)) for r in range(r)) + 2, max_width) for c in range(c)]

    def build_border() -> str:
        """Format a horizontal border.

        Returns:
            The built border.

        """
        return joint + joint.join(tborder * w for w in col_widths) + joint

    def build_row(row: list) -> str:
        """Format a row with a border.

        Args:
            row (list): the content to format.

        Returns:
            A formatted row.

        """
        cells = [truncate(str(row[c]), col_widths[c]).center(col_widths[c]) for c in range(c)]
        return sep + sep.join(cells) + sep

    lines = [build_border(), build_row(headers), build_border()]
    lines.extend([build_row(row) for row in table[1:]])
    lines.append(build_border())

    # fix intersections
    final_lines = []
    for line in lines:
        if line.startswith(joint):
            currline = list(line)
            for j in range(1, len(currline) - 1):
                if (
                    currline[j] == joint
                    and currline[j - 1] in {joint, sep}
                    and currline[j + 1] in {joint, sep}
                ):
                    currline[j] = joint  # intersection points
            final_lines.append("".join(currline))
        else:
            final_lines.append(line)

    return "\n".join(final_lines)

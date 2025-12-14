from colorama import Fore
from Utils.general_utils import wait

CHARTAPE = r"""0gqbmpWKBfZViX5azxo4RMFs.n}yj1DSAuHrLtdQI3OJk2Cc'9"8TvNU7 ,YP/h{lewE6:G"""
CHARTAPE_LEN = len(CHARTAPE)
VALID_LETTERS = set(CHARTAPE)


def check_validity(data: str):
    """Checks if a given string is a valid password/username

    Args:
        data: The proposed password/username

    Returns:
        True if valid, False if not

    """
    if 10 > len(data) > 30:
        return False

    for letter in data:
        if letter not in VALID_LETTERS:
            return False
    return True


def shift(letter: str, shiftval: str):
    """Shifts a letter by a number of spaces to the right

    Args:
        letter: The letter to be shifted
        shiftval: The letter representation of number of shifts

    Returns:
        The shifted letter

    """
    i = CHARTAPE.index(letter)

    shiftRight = CHARTAPE.index(shiftval)
    i += shiftRight

    return CHARTAPE[i % CHARTAPE_LEN]


def unshift(letter: str, shiftval: str):
    """Shifts a letter by a number of spaces to the left

    Args:
        letter: The letter to be shifted
        shiftval: The letter representation of number of shifts

    Returns:
        The shifted letter

    """
    i = CHARTAPE.index(letter)
    shiftLeft = CHARTAPE.index(shiftval)

    i -= shiftLeft

    if i < 0:
        i += CHARTAPE_LEN

    return CHARTAPE[i % CHARTAPE_LEN]


def scramble(data: str, key: str):
    """Vigenère cipher

    Args:
        data: The data to be scrambled
        key: The string key of the cipher

    Returns:
        The scrambled string

    """
    res = r""

    for i in range(len(data)):
        res += shift(data[i], key[i % len(key)])

    return res


def unscramble(data: str, key: str):
    """Vigenère cipher unscrambler

    Args:
        data: The data to be unscrambled
        key: The string key of the cipher

    Returns:
        The original unscrambled string

    """
    res = r""

    for i in range(len(data)):
        res += unshift(data[i], key[i % len(key)])

    return res


def findPW(unencrypted: str, encrypted: str):
    """Find the key string given the original and encrypted strings

    Args:
        unencrypted: The original string
        encrypted: The string after being scrambled

    Returns:
        The key string of the cipher

    """
    pw = r""
    for i in range(len(unencrypted)):
        i1 = CHARTAPE.index(unencrypted[i])
        i2 = CHARTAPE.index(encrypted[i])
        # find the diff between each letter

        shift = 0
        if i2 > i1:
            shift = i2 - i1
        elif i2 < i1:
            shift = (i2 + CHARTAPE_LEN) - i1
        else:
            shift = 0

        pw += CHARTAPE[shift]

    return pw


def verify_existing_user(username: str, encrypted_username: str):
    """Prompt for password until correct for existing user.

    Args:
        username: The username of the current user
        encrypted_username: The stored encrypted username of the current user with their password

    Returns:
        The correct password once verified

    """
    while True:
        password = input(center_wr_to_terminal_size(f"Password for {username}: ", colors=[Fore.BLUE])).strip()
        if not password:
            print(center_wr_to_terminal_size("Password cannot be empty.", colors=[Fore.RED]))
            continue

        # scramble username with password
        test_encrypted = scramble(username, password)
        if test_encrypted == encrypted_username and len(password) == len(username):
            print(center_wr_to_terminal_size("Password correct!", colors=[Fore.GREEN]))
            return password
        else:
            print(center_wr_to_terminal_size("Invalid password, try again.", colors=[Fore.RED]))

        wait(1)
        clear_prev_n_lines(2)


def register_new_user(username: str):
    """Prompt for valid password and confirmation for new user.

    Args:
        username: The username of the new user

    Returns:
        The confirmed password.

    """
    while True:
        password = input(center_wr_to_terminal_size(f"Enter new password for {username}: ", colors=[Fore.BLUE])).strip()
        confirm = input(center_wr_to_terminal_size("Confirm password: ", colors=[Fore.BLUE])).strip()
        if not password:
            print(center_wr_to_terminal_size("Password cannot be empty.", colors=[Fore.RED]))

            wait(1)
            clear_prev_n_lines(3)
        elif len(password) != len(username):
            print(center_wr_to_terminal_size("Password must have the same length as username", colors=[Fore.RED]))

            wait(1)
            clear_prev_n_lines(3)
        elif password != confirm:
            print(center_wr_to_terminal_size("Passwords do not match. Try again.", colors=[Fore.RED]))

            wait(1)
            clear_prev_n_lines(3)
        elif not check_validity(password):
            print(
                center_wr_to_terminal_size("Invalid password. Please only use alphanumeric symbols", colors=[Fore.RED]),
            )

            wait(1)
            clear_prev_n_lines(3)
        else:
            print(center_wr_to_terminal_size("Password confirmed!", colors=[Fore.GREEN]))

            wait(1)
            clear_prev_n_lines(3)

            return password


def get_valid_username():
    """Prompts the user for a valid username

    Returns:
        The username, once verified to be valid

    """
    username = input(
        center_wr_to_terminal_size("Username (leave blank for guest): [10-30 characters] -> ", colors=[Fore.BLUE]),
    )

    if not username:
        return "GUEST"

    while not check_validity(username):
        print(center_wr_to_terminal_size("Sorry, that is an invalid username...", colors=[Fore.RED]))
        wait(1)
        clear_prev_n_lines(2)
        username = input(
            center_wr_to_terminal_size("Username (leave blank for guest): [10-30 characters] -> ", colors=[Fore.BLUE]),
        )

    return username

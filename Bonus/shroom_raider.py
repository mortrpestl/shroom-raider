from Utils.central_imports import *
from colorama import Fore, Style
from Bonus_Classes.security import findPW, scramble, unscramble
from Bonus_Classes.PlayerData import PlayerData
from Bonus_Classes.Leaderboard import (
    show_personal_leaderboard,
    show_general_leaderboard,
    show_level_leaderboard,
)
from Utils.sounds import initAll


# ! NOTE: Rehash the system for boxing text like LEVEL SELECT (e.g. automate it so we don't have to do it manually.)

HERE = os.path.dirname(__file__)
SHROOM_SCRIPT = os.path.join(HERE, "game.py")
AFTER_GAME_OPTIONS = {
    'r': 'replay level',
    'm': 'main menu',
    's': 'View Statistics',
    'p': 'Personal Leaderboard',
    'g': 'General Leaderboard',
    'l': 'Level Leaderboard',
    'q': 'Quit Launcher'
}
OPTIONS_LIST = ['r', 'm', 's', 'p', 'g', 'l', 'q']

# * Advanced Helper Functions

def show_statistics(player_data):
    if player_data is None:
        print("No statistics available.")
    else:
        print("\nPlayer statistics:")
        print(player_data)


# * Level List Helper Functions


def print_levels_table(levels, selected = 1):
    """
    Print a summary of the levels.
    """
    print(r"""
⠀⢀⡀⠀⠀⢀⣀⣠⣀⠀⣀⠀⢀⣤⡄⢀⣀⣠⣀⠄⣠⠀⠀⠀⠀⠀⠀⠀⡠⣤⡀⢀⣄⣠⣄⡀⢀⡀⠀⠀⢀⣀⣠⣀⠀⠀⢀⣠⡀⠀⣠⣤⣄⣀⠄
⠐⢻⡇⠀⠐⢻⡏⠉⠁⠚⣿⡄⠁⢹⡟⢻⡏⠉⠁⠐⢿⡇⠀⠀⠀⠀⢀⣾⡉⠛⠁⢻⡏⠉⠁⠐⢳⡇⠀⠐⢻⡏⠉⠁⠀⣰⠉⠹⡿⠞⠉⣿⠋⠁⠀
⠀⢸⡇⠀⠀⢸⡷⠶⠖⠀⢸⣷⠀⣼⠁⢸⡷⠶⠖⠀⢸⡇⠀⠀⠀⠀⠀⠛⢿⣦⡀⢸⣷⠶⠖⠀⢸⡇⠀⠀⢸⡷⠶⠖⠀⣿⠀⠀⠀⠀⠀⣿⠀⠀⠀
⠀⢸⣇⣀⡀⢸⣧⣀⣀⠀⠀⣿⣶⠇⠀⢸⣧⣀⡠⠀⣼⣇⣀⠄⠀⠀⢠⣢⣀⣹⠇⢸⣧⣀⣀⠄⢸⣧⣀⡀⢸⣧⣀⣀⠀⢿⣧⣀⣀⠄⠀⣿⣀⠀⠀
⠀⠊⠙⠊⠀⠈⠙⠓⠁⠀⠀⠘⠁⠀⠀⠊⠙⠛⠁⠀⠋⠛⠃⠀⠀⠀⠈⠛⠋⠁⠀⠘⠙⠓⠁⠀⠊⠙⠊⠀⠈⠙⠓⠁⠀⠈⠙⠓⠁⠀⠀⠘⠀⠀⠀
""")

    headers = ["ID", "Title", "Description", "Difficulty"]
    rows = []
    for lvl in levels:
        rows.append(
            [
                str('　' if lvl.get('id', '') != selected else '🧑') ,
                str(lvl.get("title", "")),
                str(lvl.get("description", "")).replace("\n", " "),
                str(lvl.get("difficulty", "Normal")),
            ]
        )

    col_widths = []
    for i, h in enumerate(headers):
        max_cell = max(len(row[i]) for row in rows)
        col_widths.append(max(len(h), max_cell))

    header_line = " | ".join(h.ljust(col_widths[i]) for i, h in enumerate(headers))
    inner_width = len(header_line) + 2

    print("+" + "-" * inner_width + "+")  # top
    print(f"| {header_line} |")
    print("|" + "-" * inner_width + "|")

    for row in rows:
        row_line = " | ".join(row[i].ljust(col_widths[i]) for i in range(len(headers)))
        print(f"| {row_line} |")

    print("+" + "-" * inner_width + "+")  # bottom

def print_folders_table(folders, selected = 1):
    print("""
⠀⣀⣠⣄⡀⠀⢠⣄⠀⠀⡄⠀⠀⢀⡄⢠⣄⠀⢀⣄⣠⣄⠀⣀⠀⣠⡀⠀⠀⠀⠀⡠⣤⡀⢠⣀⠤⡠⢀⡄⠀⠀⢀⣀⠤⡠⠀⠀⡠⣄⠀⣠⣤⣄⡠
⠈⣿⠉⠉⠀⡔⠉⢿⣷⠚⡇⠀⠀⢹⡏⠉⢿⡇⢹⡏⠉⠁⠈⣿⠊⢻⡇⠀⠀⠀⣼⣍⠙⠀⢹⡏⠉⠀⠛⡇⠀⠀⢹⡏⠉⠀⢀⠎⠘⠿⠋⠈⣿⠉⠀
⠀⣿⠶⠖⢸⣧⠀⠘⡿⠀⡇⠀⠀⢸⡇⠀⠘⡇⢸⡿⠶⠂⠀⣿⢀⡞⠀⠀⠀⠀⠙⢿⣷⡄⢸⡷⠶⠂⠀⡇⠀⠀⢸⡷⠶⠂⢸⡆⠀⠀⠀⠀⣿⠀⠀
⠀⣟⡄⠀⠀⢿⢷⠔⠁⠀⣷⣤⡄⢸⣧⣀⡰⠁⢰⣧⡤⡤⠀⣿⡤⢿⢄⠀⠀⠀⣾⣄⣹⠃⢸⣧⣤⠄⢀⣧⣄⠄⢸⢧⣤⠄⠸⣿⣄⣀⠀⠀⣟⠄⠀
⠀⠈⠀⠀⠀⠀⠁⠀⠀⠈⠉⠉⠀⠈⠉⠉⠀⠀⠈⠉⠉⠀⠀⠉⠀⠈⠁⠀⠀⠀⠉⠉⠀⠀⠈⠉⠉⠀⠈⠉⠉⠀⠈⠉⠉⠀⠀⠈⠉⠁⠀⠀⠉⠀⠀
""")
    headers = ["ID", "Title", "Description"]
    rows = []
    for folder in folders:
        rows.append(
            [
                str('　' if folder.get('id', '') != selected else '🧑') ,
                str(folder.get("title", "")),
                str(folder.get("description", "")).replace("\n", " "),
            ]
        )

    col_widths = []
    for i, h in enumerate(headers):
        max_cell = max(len(row[i]) for row in rows)
        col_widths.append(max(len(h), max_cell))

    header_line = " | ".join(h.ljust(col_widths[i]) for i, h in enumerate(headers))
    inner_width = len(header_line) + 2

    print("+" + "-" * inner_width + "+")  # top
    print(f"| {header_line} |")
    print("|" + "-" * inner_width + "|")

    for row in rows:
        row_line = " | ".join(row[i].ljust(col_widths[i]) for i in range(len(headers)))
        print(f"| {row_line} |")

    print("+" + "-" * inner_width + "+")

def print_after_game_options(selected):
    option = OPTIONS_LIST[selected]
    headers = ['option', 'description']
    rows = []
    for o in AFTER_GAME_OPTIONS:
        rows.append(
            [
                '　' if o != option else '🧑', 
                AFTER_GAME_OPTIONS[o]
            ]
        )

    col_widths = []
    for i, h in enumerate(headers):
        max_cell = max(len(row[i]) for row in rows)
        col_widths.append(max(len(h), max_cell))

    header_line = " | ".join(h.ljust(col_widths[i]) for i, h in enumerate(headers))
    inner_width = len(header_line) + 2

    print("+" + "-" * inner_width + "+")  # top
    print(f"| {header_line} |")
    print("|" + "-" * inner_width + "|")

    for row in rows:
        row_line = " | ".join(row[i].ljust(col_widths[i]) for i in range(len(headers)))
        print(f"| {row_line} |")

    print("+" + "-" * inner_width + "+")

# * Level Selection and Launching Functions


def choose_level(levels):
    """
    Displays Level Select menu and returns chosen level dict or None on quit.
    """

    # if no levels
    clear_terminal()
    if not levels:
        print("No levels found in Levels/")
        return None

    # if there is levels
    selected = 1
    print_levels_table(levels, selected)
    while True:
        choice = m()
        if choice is not None:
            if choice == "Q":
                return "q"
            if choice == '!':
                return '!'
            if choice == 'enter':
                return (selected, levels[selected - 1])
            if choice == 'w':
                if selected > 1:
                    selected -= 1
                    clear_terminal()
                    print_levels_table(levels, selected)
            elif choice == 's':
                if selected < len(levels):
                    selected += 1
                    clear_terminal()
                    print_levels_table(levels, selected)

def choose_folder(folders):
    
    # if no levels
    clear_terminal()
    if not folders:
        print("Walang folders boss")
        return None

    # if there is levels
    
    selected = 1
    print_folders_table(folders, selected)
    while True:
        choice = m()
        if choice is not None:
            if choice == "Q":
                return "q"
            if choice == 'enter':
                return selected
            if choice == 'w':
                if selected > 1:
                    selected -= 1
                    clear_terminal()
                    print_folders_table(folders, selected)
            elif choice == 's':
                if selected < len(folders):
                    selected += 1
                    clear_terminal()
                    print_folders_table(folders, selected)

def choose_after_game_option():
    clear_terminal()
    
    selected = 0
    print_after_game_options(selected)
    while True:
        choice = m()
        if choice is not None:
            if choice == 'enter':
                return selected
            if choice == 'w':
                if selected > 0:
                    selected -= 1
                    clear_terminal()
                    print_after_game_options(selected)
            elif choice == 's':
                if selected < len(OPTIONS_LIST)-1:
                    selected += 1
                    clear_terminal()
                    print_after_game_options(selected)


def make_stage_file_from_grid(grid_text):
    """
    Creates: the file to send to shroom_raider.py from grid_text.
    Returns: path to this temporary file, for sending to shroom_raider.py
    """
    if not grid_text.strip():
        raise ValueError("Empty grid")

    content = grid_text.strip() + "\n"
    fd, path = tempfile.mkstemp(prefix="stage_", suffix=".txt", dir=HERE)
    os.close(fd)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return path


def launch_game_with_level(level):
    """
    Send the level to shroom_raider.py
    """
    
    # create temp files to store level
    stage_path = make_stage_file_from_grid(level["grid"])
    report_fd, report_path = tempfile.mkstemp(
        prefix="shroom_report_", suffix=".json", dir=HERE
        )
    os.close(report_fd)

    try:
        # run game
        cmd = [sys.executable, SHROOM_SCRIPT, "-f", stage_path, "-R", report_path]

        # optional dark mode parameter
        if "dark_radius" in level and level["dark_radius"] is not None:
            cmd += ["-d", str(level["dark_radius"])]

        # optional bee_data parameter
        if "bee_data" in level and level["bee_data"]:
            cmd += ["--bee_data", str(level["bee_data"])]

        print(f"\nRunning: {' '.join(cmd)}\n")
        return_code = subprocess.call(cmd)

        # load report
        report = None
        if os.path.getsize(report_path) > 0:
            with open(report_path, "r", encoding="utf-8") as f:
                report = json.load(f)
        return return_code, report
    finally:
        # cleans up temp files
        for path in (stage_path, report_path):
            if os.path.exists(path):
                os.remove(path)

# * Password Methods
def verify_existing_user(username: str, encrypted_username: str) -> str:
    """
    Prompt for password until correct for existing user.
    Returns the correct password once verified.
    """
    while True:
        password = input(f"Password for {username}: ").strip()
        if not password:
            print("Password cannot be empty.")
            continue

        # scramble username with password
        test_encrypted = scramble(username, password)
        if test_encrypted == encrypted_username:
            print("Password correct!")
            return password
        else:
            print("Invalid password, try again.")


def register_new_user(username: str) -> str:
    """
    Prompt for password and confirmation for new user.
    Returns the confirmed password.
    """
    while True:
        password = input(f"Enter new password for {username}: ").strip()
        confirm = input("Confirm password: ").strip()
        if not password:
            print("Password cannot be empty.")
        elif password != confirm:
            print("Passwords do not match. Try again.")
        else:
            print("Password confirmed!")
            return password

# gameplay start + loop
def main():
    with open("Assets/UI/TitleScreenIntro.txt", "r", encoding="unicode_escape") as intro:
        typewriter(intro.read(), 15)
    with open("Assets/UI/TitleScreenArt.txt", "r", encoding="utf+8") as art:
        load_in(Fore.RED + "\n" + art.read() + Style.RESET_ALL, 5)

    username = input("Username (leave blank for guest): ").strip() or "GUEST"

    encrypted_username, reference_username = PlayerData.lookup_excel_username(username)

    if encrypted_username:  # existing user
        password = verify_existing_user(username, encrypted_username)
    else:  # new user
        password = register_new_user(username)
        # store encrypted username & reference username in Excel
        encrypted_username = scramble(username, password)
        PlayerData.store_new_user(username, encrypted_username)

    player_data = PlayerData(username, password) 

    b()
    initAll()
    while True: # folders muna tayo
        path = []
        folders = LevelManager.load_folders()
        folder_choice = choose_folder(folders)

        if folder_choice == "q":
            print("Quitting launcher.")
            exit(ExitCodes.QUIT.value)

        path.append(folder_choice)

        while True:
            levels = LevelManager.load_levels(folder_choice)
            level_choice = choose_level(levels)

            if level_choice == 'q':
                print("Quitting launcher.")
                exit(ExitCodes.QUIT.value)
            elif level_choice == '!':
                break

            path = [folder_choice]
            path.append(level_choice[0])

            while True: 
                #session start
                start_time = time.time()
                return_code, report = launch_game_with_level(level_choice[1])
                end_time = time.time()
                wait(1.25)
                clear_terminal()
                # session end

                FULL_ID = '/'.join(str(x) for x in path)
                # process session data
                if report:
                    elapsed_time = float(end_time - start_time)
                    player_data.apply_report_dict(
                        report,
                        return_code=return_code,
                        level_id=FULL_ID,
                        elapsed_time=elapsed_time,
                    )

                while True:
                    choice = choose_after_game_option()
                    choice = OPTIONS_LIST[choice]
                    match choice:
                        case "r" | "m":
                            break
                        case "s":
                            show_statistics(player_data)
                            continue
                        case "q":
                            print("Quitting launcher.")
                            exit(ExitCodes.QUIT.value)
                        case "p":
                            show_personal_leaderboard(player_data)
                            continue
                        case "g":
                            show_general_leaderboard()
                            continue
                        case "l":
                            show_level_leaderboard(FULL_ID)
                            continue
                        case _:
                            print("Invalid choice, try again.")

                if choice in ("r", "replay"):
                    continue  # continue playing the level
                if choice in ("m", "menu"):  # stop and go back to menu
                    clear_terminal()
                    break


if __name__ == "__main__":
    argument_parser = ap()
    argument_parser.add_argument("-f", "--stage_file")
    argument_parser.add_argument("-d", "--darkness_radius", default=None)
    argument_parser.add_argument("-R", "--report_file", default=None)
    args = argument_parser.parse_args()

    if args.stage_file is not None: # if they wanna be weird and test just the game out
        cmd = [sys.executable, SHROOM_SCRIPT, "-f", args.stage_file]

        # optional dark mode parameter
        if args.darkness_radius is not None:
            cmd += ["-d", str(args.darkness_radius)]

        # optional report parameter
        if args.report_file is not None:
            cmd += ["-R", str(args.report_file)]

        print(f"\nRunning: {' '.join(cmd)}\n")
        return_code = subprocess.call(cmd)

    else:
        main()

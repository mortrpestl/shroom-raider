import json
import os
import pathlib
import subprocess
import sys
import tempfile
import time
import os
from argparse import ArgumentParser as ap

import LevelManager
from Bonus_Classes.Leaderboard import (
    show_general_leaderboard,
    show_level_leaderboard,
    show_personal_leaderboard,
)
from Bonus_Classes.PlayerData import PlayerData
from Bonus_Classes.security import get_valid_username, register_new_user, scramble, verify_existing_user
from colorama import Back, Fore
from Utils.animator import load_in, progress_bar, typewriter
from Utils.Enums import ExitCodes
from Utils.general_utils import center_wr_to_terminal_size, clear_terminal, wait
from Utils.movement import block_keys as b
from Utils.movement import menu_movement as m
from Utils.sounds import initAll

import Utils.sounds as s

HERE = os.path.dirname(__file__)
SHROOM_SCRIPT = os.path.join(HERE, "game.py")
AFTER_GAME_OPTIONS = {
    "r": "Replay Level",
    "m": "Return To Main Menu",
    "s": "View Player Statistics",
    "p": "Personal Leaderboard",
    "g": "General Leaderboard",
    "l": "Level Leaderboard",
    "q": "Quit Launcher",
}
OPTIONS_LIST = ["r", "m", "s", "p", "g", "l", "q"]

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

# * Advanced Helper Functions


def show_statistics(player_data: PlayerData):
    """Prints the player's stats if they exist

    Args:
        playerdata: A PlayerData object

    """
    if player_data is None:
        print("No statistics available.")
    else:
        print("\nPlayer statistics:")
        print(player_data)


# * Level List Helper Functions


def print_levels_table(levels: dict, selected: int = 1, completed_lvl_ids=set(), folder: dict | None = None):
    """Print a summary of the levels.

    Args:
        levels: The levels to be printed
        selected: The current level to be highlighted for selection
        completed_lvl_ids: The completed levels by this player

    """
    display = []
    with open("Assets/UI/LevelSelectArt.txt", encoding="utf+8") as art:
        display.append(center_wr_to_terminal_size(art.read(), colors=[Fore.GREEN]))
    display.append("[w] Up | [s] Down | [Q] Quit Launcher | [Enter] Go to | [!] Go Back\n")
    spanner = "---===x{🌲}x===---\n"

    display.append(spanner)
    for lvl in levels:
        checked = '✔' if lvl.get("id", "") in completed_lvl_ids else ''
        if lvl.get("id", "") == selected:
            display.append(
                center_wr_to_terminal_size(f" {checked} <🧑 {lvl.get('title', '')} 🧑>", colors=[Back.GREEN, Fore.BLACK]),
            )
            desc = str(lvl.get("description", "")).replace("\n", " ") + "\n"
            difficulty = str(lvl.get("difficulty", "Normal")) + "\n"
        elif lvl.get("id", "") in completed_lvl_ids:
            display.append(center_wr_to_terminal_size(f"{checked} {lvl.get('title', '')}", colors=[Fore.GREEN]))
        else:
            display.append(str(lvl.get("title", "")))
    display.append("\n" + spanner)

    display.append(center_wr_to_terminal_size("Difficulty: " + difficulty, colors=[Fore.RED]))
    display.append(center_wr_to_terminal_size("Description:\n" + desc, colors=[Fore.BLUE]))

    if folder and folder.get("song_name"):
        display.append(center_wr_to_terminal_size(f"Song Playing:\n {folder.get('song_name')}\n", colors=[Fore.LIGHTBLUE_EX]))

    clear_terminal()
    print(center_wr_to_terminal_size("\n".join(display)))


def print_folders_table(folders: dict, selected: int = 1):
    """Print a summary of the folders.

    Args:
        folders: The folders to be printed
        selected: The current folder to be highlighted for selection

    """
    display = []
    with open("Assets/UI/FolderSelectArt.txt", encoding="utf+8") as art:
        display.append(center_wr_to_terminal_size(art.read(), colors=[Fore.RED]))
    display.append("[w] Up | [s] Down | [Q] Quit Launcher | [Enter] Go to\n")
    spanner = "---===x{🔥}x===---\n"

    display.append(spanner)
    for folder in folders:
        if folder.get("id", "") == selected:
            display.append(
                center_wr_to_terminal_size(f"<🧑 {folder.get('title', '')} 🧑>", colors=[Back.GREEN, Fore.BLACK]),
            )
            desc = str(folder.get("description", "")).replace("\n", " ") + "\n"
        else:
            display.append(str(folder.get("title", "")))
    display.append("\n" + spanner)

    display.append(center_wr_to_terminal_size("Description:\n" + desc, colors=[Fore.BLUE]))

    clear_terminal()
    print(center_wr_to_terminal_size("\n".join(display)))


def print_after_game_options(selected: int, folder : int):
    """Prints the after-level menu

    Args:
        selected: The currently selected option to be highlighted

    """

    display = []
    with open("Assets/UI/MainMenuArt.txt", encoding="utf+8") as art:
        display.append(center_wr_to_terminal_size(art.read(), colors=[Fore.YELLOW]))

    option = OPTIONS_LIST[selected]

    display.append("[w] Up | [s] Down | [Enter] Go to\n")

    spanner = "---===x{🪓}x===---\n"
    display.append(spanner)
    for o in AFTER_GAME_OPTIONS:
        if o == option:
            display.append(
                center_wr_to_terminal_size(f"<🧑 {AFTER_GAME_OPTIONS[o]} 🧑>", colors=[Back.GREEN, Fore.BLACK]),
            )
        else:
            display.append(AFTER_GAME_OPTIONS[o])
    display.append("\n" + spanner)

    display.append(center_wr_to_terminal_size(f"\nSong Playing:\n{folder.get('song_name')}\n", colors=[Fore.LIGHTBLUE_EX]))

    clear_terminal()
    print(center_wr_to_terminal_size("\n".join(display)))


# * Level Selection and Launching Functions


def choose_level(levels: dict, completed_lvl_ids: set, folder: dict | None = None, selected: int = 1):
    """Displays level select menu for user to choose level

    Args:
        levels: A dictionary of levels
        completed_level_ids: A set of all the levels this player has completed

    Returns:
        The level selected and its index if there is a chosen level. Else, it returns exit codes to be interpreted later

    """
    # if no levels
    clear_terminal()
    if not levels:
        print("No levels found in Levels/")
        return None

    # if there is levels
    print_levels_table(levels, selected, completed_lvl_ids, folder)
    while True:
        choice = m()
        if choice is not None:
            if choice == "Q":
                return "q", selected
            if choice == "!":
                return "!", selected
            if choice == "enter":
                return (selected, levels[selected - 1]), selected
            if choice == "w":
                if selected > 1:
                    selected -= 1
                    clear_terminal()
                    print_levels_table(levels, selected, completed_lvl_ids, folder)
            elif choice == "s":
                if selected < len(levels):
                    selected += 1
                    clear_terminal()
                    print_levels_table(levels, selected, completed_lvl_ids, folder)


def choose_folder(folders: dict, selected : int):
    """Displays folder select menu for user to choose folder

    Args:
        folders: A dictionary of folders

    Returns:
        The folder selected and its index if there is a chosen folder. Else, it returns exit codes to be interpreted later

    """
    # if no levels
    clear_terminal()
    if not folders:
        print("Sorry, there are no folders")
        return None, None

    # if there is levels

    print_folders_table(folders, selected)
    while True:
        choice = m()
        if choice is not None:
            if choice == "Q":
                return "q", None
            if choice == "enter":
                return selected, selected
            if choice == "w":
                if selected > 1:
                    selected -= 1
                    clear_terminal()
                    print_folders_table(folders, selected)
            elif choice == "s":
                if selected < len(folders):
                    selected += 1
                    clear_terminal()
                    print_folders_table(folders, selected)


def choose_after_game_option(curr_display: str | None, folder_choice : int):
    """Shows the after-game menu to the user

    Args:
        curr_display: The display (leaderboards, stats, etc) to be shown after the menu

    """
    blank = center_wr_to_terminal_size("Nothing to show...", colors=[Fore.BLUE])
    clear_terminal()

    selected = 0
    print_after_game_options(selected, folder_choice)
    print(curr_display or blank)
    while True:
        choice = m()
        if choice is not None:
            if choice == "enter":
                return selected
            if choice == "w":
                if selected > 0:
                    selected -= 1

            elif choice == "s":
                if selected < len(OPTIONS_LIST) - 1:
                    selected += 1

            clear_terminal()
            print_after_game_options(selected, folder_choice)
            print(curr_display or blank)


def make_stage_file_from_grid(grid_text: str):
    """Makes a stage file to be run

    Args:
        grid_text: The input string to be made into a stage file

    Returns:
        The path to the created stage file

    """
    if not grid_text.strip():
        raise ValueError("Empty grid")

    content = grid_text.strip() + "\n"
    fd, path = tempfile.mkstemp(prefix="stage_", suffix=".txt", dir=HERE)
    os.close(fd)
    pathlib.Path(path).write_text(content, encoding="utf-8")
    return path


def launch_game_with_level(level: dict):
    """Send the level to game.py for running

    Args:
        level: A dictionary of the current level data

    Returns:
        The return code for the level, as well as the report of the game played

    """
    # create temp files to store level
    stage_path = make_stage_file_from_grid(level["grid"])
    report_fd, report_path = tempfile.mkstemp(prefix="shroom_report_", suffix=".json", dir=HERE)
    os.close(report_fd)

    try:
        # run game
        cmd = [sys.executable, SHROOM_SCRIPT, "-f", stage_path, "-R", report_path]

        # optional dark mode parameter
        if "dark_radius" in level and level["dark_radius"] is not None:
            cmd += ["-d", str(level["dark_radius"])]

        # optional bee_data parameter
        if level.get("bee_data"):
            cmd += ["--bee_data", str(level["bee_data"])]

        bgm_file, song_name = level.get("bgm"), level.get("song_name")
        cmd += ["-M", str(bgm_file)]
        cmd += ["-S", str(song_name)]

        s.current_bgm_stop()

        # print(f"\nRunning: {' '.join(cmd)}\n")

        # ! You can integrate loading screen feature here
        progress_bar("Loading your level...", total_time=0.2)
        return_code = subprocess.call(cmd)

        # load report
        report = None
        if pathlib.Path(report_path).stat().st_size > 0:
            with open(report_path, encoding="utf-8") as f:
                report = json.load(f)
        return return_code, report
    finally:
        # cleans up temp files
        for path in (stage_path, report_path):
            if pathlib.Path(path).exists():
                pathlib.Path(path).unlink()


# gameplay start + loop
def main():

    """Handles the main gameplay loop from user login, folder and level selection, and data storage
    """
    clear_terminal()
    initAll()
    s.current_bgm_stop()

    s.welcome_sound()
    
    with open("Assets/UI/TitleScreenIntro.txt", encoding="unicode_escape") as intro:
        typewriter(intro.read(), 6)
    with open("Assets/UI/TitleScreenArt.txt", encoding="utf+8") as art:
        load_in(art.read(), 3, colors=[Fore.RED], colors2=[Fore.YELLOW], mode="--alternate")

    username = get_valid_username()

    encrypted_username, reference_username = PlayerData.lookup_excel_username(username)

    if encrypted_username and username != "GUEST":  # existing user
        password = verify_existing_user(username, encrypted_username)
        player_data = PlayerData(username, password)
    elif username == "GUEST":
        player_data = PlayerData("GUEST", "guest")
    else:
        password = register_new_user(username)
        # store encrypted username & reference username in Excel
        player_data = PlayerData(username, password)

    b()
    progress_bar("\nStarting Game...")

    s.welcome_sound_stop()

    SELECTED = 1

    while True:  # folders muna tayo
        s.mainmenu_sound()
        path = []
        folders = LevelManager.load_folders()
        folder_choice, SELECTED = choose_folder(folders, SELECTED)

        if folder_choice == "q":
            s.fadeout_all_sounds(1000)
            progress_bar("Quitting launcher.", total_time=1)
            exit(ExitCodes.QUIT.value)

        path.append(folder_choice)

        s.folder_bgm_sound(folder_choice)
        
        LEVEL_SELECTED = 1
        
        while True:

            levels = LevelManager.load_levels(folder_choice)
            try:
                current_folder = folders[folder_choice-1]
                level_choice, LEVEL_SELECTED = choose_level(
                    levels,
                    player_data.get_completed_lvl_ids_by_folder_id(folder_choice),
                    folder=current_folder,
                    selected = LEVEL_SELECTED
                    )
            except:
                level_choice, LEVEL_SELECTED = choose_level(levels, set(), folder=None, selected=LEVEL_SELECTED)
            if level_choice == "q":
                s.fadeout_all_sounds(1000)
                progress_bar("Quitting launcher.", total_time=1)
                exit(ExitCodes.QUIT.value)
            elif level_choice == "!":
                break

            path = [folder_choice]
            path.append(level_choice[0])

            while True:
                # session start
                start_time = time.time()
                return_code, report = launch_game_with_level(level_choice[1])
                end_time = time.time()
                wait(1.25)
                clear_terminal()
                # session end

                s.folder_bgm_sound(folder_choice)
                
                FULL_ID = "/".join(str(x) for x in path)
                # process session data
                if report:
                    elapsed_time = float(end_time - start_time)
                    player_data.apply_report_dict(
                        report,
                        return_code=return_code,
                        level_id=FULL_ID,
                        elapsed_time=elapsed_time,
                    )
                curr_display = ""
                while True:
                    choice = choose_after_game_option(curr_display, current_folder)
                    choice = OPTIONS_LIST[choice]
                    print()

                    match choice:
                        case "r" | "m":
                            break
                        case "s":
                            progress_bar("Loading your statistics...", 0.5)
                            curr_display = repr(player_data)
                            continue
                        case "q":
                            s.fadeout_all_sounds(1000)
                            progress_bar("Quitting launcher.", total_time=1)
                            exit(ExitCodes.QUIT.value)
                        case "p":
                            progress_bar("Loading leaderboard...", 0.5)
                            curr_display = show_personal_leaderboard(player_data)
                            continue
                        case "g":
                            progress_bar("Loading leaderboard...", 0.5)
                            curr_display = show_general_leaderboard()
                            continue
                        case "l":
                            progress_bar("Loading leaderboard...", 0.5)
                            curr_display = show_level_leaderboard(FULL_ID)
                            continue
                        case _:
                            print("Invalid choice, try again.")

                if choice in ("r", "replay"):
                    continue  # continue playing the level
                if choice in ("m", "menu"):  # stop and go back to menu
                    progress_bar("Going back to main menu...", 0.5)
                    clear_terminal()
                    break


if __name__ == "__main__":
    argument_parser = ap()
    argument_parser.add_argument("-f", "--stage_file")
    argument_parser.add_argument("-d", "--darkness_radius", default=None)
    argument_parser.add_argument("-R", "--report_file", default=None)
    argument_parser.add_argument("-M", "--bgm", default="default_level_music.mp3")
    args = argument_parser.parse_args()

    if args.stage_file is not None:  # if they wanna be weird and test just the game out
        cmd = [sys.executable, SHROOM_SCRIPT, "-f", args.stage_file]

        # optional dark mode parameter
        if args.darkness_radius is not None:
            cmd += ["-d", str(args.darkness_radius)]

        # optional report parameter
        if args.report_file is not None:
            cmd += ["-R", str(args.report_file)]

        cmd += ["-M", str(args.bgm)]

    else:
        main()

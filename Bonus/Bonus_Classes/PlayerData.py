import json
import os
import time

import pandas as pd
from LevelManager import get_level_title
from Utils.Enums import ExitCodes
from Utils.general_utils import format_time, tabulate

from .security import findPW, scramble, unscramble

HERE = os.path.dirname(__file__)
EXCEL_FILE = os.path.abspath(os.path.join(HERE, "..", "Statistics", "PlayerData.xlsx"))
HEADERS = [
    "username",
    "encrypted_username",
    "total_mushrooms_collected",
    "total_tiles_walked",
    "total_wins",
    "total_times",
    "total_seconds_played",
    "completed_data",
]

# ! TODO: documentation


def decrypt(dict: dict[str, int], key: str) -> dict[str, int]:
    """Decrypts a dictionary of player data given a key.

    Args:
        dict: The dictionary containing the player data
        key: The key used to decrypt the dictionary's contents

    Returns:
        A dict containing the decrypted entries of player data

    """
    return {k: unscramble(str(v), key) for k, v in dict.items()}


def encrypt(dict: dict[str, int], key: str) -> dict[str, int]:
    """Encrypts a dictionary of player data given a key.

    Args:
        dict: The dictionary containing the player data
        key: The key used to encrypt the dictionary's contents

    Returns:
        A dict containing the encrypted entries of player data

    """
    return {k: scramble(str(v), key) for k, v in dict.items()}


# * Pandas helpers


def read_raw_rows() -> dict:
    """Reads all player rows from Excel without decryption.
    Used for reading data in encrypted form.

    Returns:
        The raw data (no decryption) in the Excel file transcribed as dictionary.

    """
    df = pd.read_excel(EXCEL_FILE, engine="openpyxl")
    rows = df.to_dict(orient="records")

    for r in rows:
        cd = r.get("completed_data", "{}")
        if pd.isna(cd) or not cd or str(cd).strip().lower() == "nan":
            r["completed_data"] = "{}"

    return rows


def read_all_rows() -> dict:
    """Reads all player rows from Excel and decrypts all fields.
    Used for displaying/reading data, never for saving.

    Returns:
        The decrypted data in the Excel file transcribed as dictionary.

    """
    rows = read_raw_rows()

    for r in rows:
        unencrypted_name = r.get("username")
        encrypted_name = r.get("encrypted_username")

        if unencrypted_name and encrypted_name and unencrypted_name != encrypted_name:
            try:
                pw = findPW(unencrypted_name, encrypted_name)
                decrypted = decrypt(
                    {k: str(v) for k, v in r.items() if k not in ("username", "encrypted_username")},
                    pw,
                )
                decrypted["username"] = unencrypted_name
                decrypted["encrypted_username"] = encrypted_name
                r.update(decrypted)
            except Exception as e:
                print(f"Failed to decrypt for {unencrypted_name}: {e}")

    return rows


def write_all_rows(rows: dict[str, int]):
    """Writes all player rows (encrypted) back to Excel.
    """
    pd.DataFrame(rows, columns=HEADERS).to_excel(EXCEL_FILE, index=False, engine="openpyxl")


def safe_int(value: str | int) -> int:
    """Parses empty entries into integers if needed.
    """
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return 0
    try:
        return int(value)
    except (ValueError, TypeError):
        return 0


# * Actual Class Declaration


class PlayerData:
    """Handles the storing and sending of session data for each game session for a given player.
    Also handles distribution of global player information to leaderboards.

    Args:
        name: A string denoting the name of the player
        password: A string denoting the password of the player
        total_mushrooms_collected: An int denoting the total mushrooms collected by the player
        total_tiles_walked: An int denoting the total number of tiles a player walked throughout thegame.
        total_wins: An int denoting the total wins a player had throughout the game.
        total_times: An int denoting the
        total_seconds_played: An int denoting the total minimum time taken by a player to beat each of their completed levels
        completed_data: A stringified JSON containing data about levels a player has completed.
        completed_levels: A dict containing data about levels a player has completed.

    """

    def __init__(self, name, password=None):
        """Initializes the player's data storage given a name.

        Args:
            name: Denotes the name of the player
            password: Denotes the password of the player, to be used in decrypting

        """
        self.name = name
        self.password = password
        self.total_mushrooms_collected = 0
        self.total_tiles_walked = 0
        self.total_wins = 0
        self.total_times = 0
        self.total_seconds_played = 0
        self.completed_data = "{}"
        self.completed_levels = {}
        self.reset_session()
        self.load_or_create()

    # * Log-In Validators

    @staticmethod
    def lookup_excel_username(username: str) -> None | str:
        """Returns a username from the database if exists and None if does not

        Returns:
            None if there is no username in the database that matches
            username if there is a username in the database that matches

        """
        # Read decrypted rows for lookup
        rows = read_all_rows()
        for r in rows:
            if r["username"] == username:
                return r.get("encrypted_username"), r["username"]
        return None, username

    @staticmethod
    def store_new_user(username: str, encrypted_username: str):
        """Stores a new username and initializes their data in the database if it does not exist in the database.

        Args:
            username: The username to store in the database.
            encrypted_username: The encrypted username to store (to find the key later).

        """
        # Read RAW rows to preserve encryption
        rows = read_raw_rows()
        rows.append({
            "username": username,
            "encrypted_username": encrypted_username,
            "total_mushrooms_collected": 0,
            "total_tiles_walked": 0,
            "total_wins": 0,
            "total_times": 0,
            "total_seconds_played": 0,
            "completed_data": "{}",
        })
        write_all_rows(rows)

    # * Getter Methods
    def get_password(self) -> str:
        """Returns the password."""
        return self.password

    # * Setter Methods
    def set_password(self, key):
        """Sets the password."""
        self.password = key

    # * Session Setter Methods
    def reset_session(self):
        """Resets the session

        Start time is recorded (to determine total length later), and win/dead conditions are set to false (as expected from any grid spawn).

        """
        self.session_mushrooms = 0
        self.session_tiles = 0
        self.session_win = False
        self.session_dead = False
        self.session_start_time = time.time()

    def record_move(self, n=1):
        """Adds number of moves to the session data."""
        self.session_tiles += n

    def record_mushroom(self, n=1):
        """Adds number of mushrooms to the session data."""
        self.session_mushrooms += n

    def record_win(self):
        """Records a win for the player"""
        self.session_win = True

    def record_death(self):
        """Records a death for the player"""
        self.session_dead = True

    def load_or_create(self):
        """Reinitializes the player's statistics based on records in the database.
        This includes initializing the data for a new player.
        """
        # Read decrypted rows to load user data
        rows = read_all_rows()
        for row in rows:
            if row["username"] == self.name:
                self.total_mushrooms_collected = safe_int(row.get("total_mushrooms_collected"))
                self.total_tiles_walked = safe_int(row.get("total_tiles_walked"))
                self.total_wins = safe_int(row.get("total_wins"))
                self.total_times = safe_int(row.get("total_times"))
                self.total_seconds_played = safe_int(row.get("total_seconds_played"))
                self.completed_data = row.get("completed_data", "{}")
                try:
                    self.completed_levels = json.loads(self.completed_data)
                except Exception:
                    self.completed_levels = {}
                return

        raw_rows = read_raw_rows()
        raw_rows.append(self.to_dict())
        write_all_rows(raw_rows)

    # * Level Completion Handler Methods
    def get_completed_levels(self) -> dict[str, int, None]:
        """Gets the completed levels of the player"""
        if not self.completed_levels and self.completed_data:
            try:
                self.completed_levels = json.loads(self.completed_data)
            except Exception:
                self.completed_levels = {}
        return self.completed_levels

    def record_level_completion(self, level_id: int, elapsed_time_ms: int):
        """Adds a completed level and the relevant player data to the player's completed data.
        If a level has been recompleted, stats can be recomputed (e.g. getting the best time).

        """
        completed = self.get_completed_levels()
        key = str(level_id)
        completed[key] = min(completed.get(key, elapsed_time_ms), elapsed_time_ms)
        self.completed_levels = completed
        self.completed_data = json.dumps(completed)

    # * Excel-Interaction Methods
    def commit_session(self, time_elapsed_ms: float):
        """Adjusts the player data given a level file.
        Also logs the updated data to the database.
        """
        self.total_mushrooms_collected += self.session_mushrooms
        self.total_tiles_walked += self.session_tiles
        self.total_times += 1
        self.total_seconds_played += time_elapsed_ms
        if self.session_win:
            self.total_wins += 1
        self.completed_data = json.dumps(self.completed_levels)
        self.save()
        self.reset_session()

    def save(self):
        """Saves player data to the database."""
        rows = read_raw_rows()

        found = False
        for r in rows:
            if r["username"] == self.name:
                r.update(
                    self.to_dict(),
                )  # to_dict() handles encryption (NOT THIS! PLEASE, PLEASE DONT CHANGE THAT FUNCTIONALITY)
                found = True
                break

        if not found:
            rows.append(self.to_dict())
        write_all_rows(rows)

    def to_dict(self):
        """Converts session data to a dict."""
        data = {
            "total_mushrooms_collected": self.total_mushrooms_collected,
            "total_tiles_walked": self.total_tiles_walked,
            "total_wins": self.total_wins,
            "total_times": self.total_times,
            "total_seconds_played": self.total_seconds_played,
            "completed_data": self.completed_data,
        }
        if self.password:
            data = encrypt(data, self.password)
            data["encrypted_username"] = scramble(self.name, self.password)
        else:
            data["encrypted_username"] = self.name
        data["username"] = self.name
        return data

    def apply_report_dict(self, report, return_code=None, level_id=None, elapsed_time=0):
        """Processes the updates to be performed after receiving a session report."""
        self.session_mushrooms = safe_int(report["mushrooms_collected"])
        self.session_tiles = safe_int(report["moves_made"])
        self.session_win = report["win"]
        self.session_dead = report["dead"]

        if self.session_win and level_id is not None:
            self.record_level_completion(level_id, elapsed_time)

        if return_code in (ExitCodes.VICTORY.value, ExitCodes.DEFEAT.value):
            if return_code == ExitCodes.VICTORY.value:
                self.record_win()
            self.commit_session(elapsed_time)
            return

        self.commit_session(elapsed_time)

    def load_report_file(self, path, level_id=None):
        """"""
        with open(path, encoding="utf-8") as f:
            report = json.load(f)
        return self.apply_report_dict(report, level_id=level_id)

    def get_completed_levels_organized(self):
        """Returns an organized dict of levels

        Returns:
            completed_levels_in_folder: an organized dict of levels with an associated folder_id

        """
        completed_levels = self.get_completed_levels()
        if not completed_levels:
            return [["None"]]
            # completed_headers = ["Completed Levels"]
        else:

            def sort_key(item):
                try:
                    folder, level = item[0].split("/")
                    return int(folder), int(level)
                except Exception:
                    return (0, 0)

            sorted_levels = sorted(completed_levels.items(), key=sort_key)
            completed_rows = [
                [
                    level_id,
                    get_level_title(*level_id.split("/")) or "-",
                    format_time(ms),
                ]
                for level_id, ms in sorted_levels
            ]
            return completed_rows

    def get_completed_lvl_ids_by_folder_id(self, folder_id) -> dict[str, int]:
        """Returns an organized dict of levels with an associated folder_id

        Args:
            folder_id: gets levels based on folder_id

        Returns:
            completed_levels_in_folder: an organized dict of levels with an associated folder_id

        """
        completed_rows = self.get_completed_levels_organized()

        if completed_rows == [["None"]]:
            return set()

        completed_levels_in_folder = set()

        for i in completed_rows:
            try:
                lvl_id = i[0].split("/")
                if int(lvl_id[0]) == folder_id:
                    completed_levels_in_folder.add(int(lvl_id[1]))
            except (ValueError, IndexError):
                continue

        return completed_levels_in_folder

    # * Display

    def __repr__(self):
        """Displays the statistics belonging to a player in an organized manner.

        Returns:
            display: a list of rows depicting the organized dict of the player statistics

        """
        stats_rows = [
            ["Player Name", self.name],
            ["Total Mushrooms", self.total_mushrooms_collected],
            ["Tiles Walked", self.total_tiles_walked],
            ["Total Wins", self.total_wins],
            ["Total Runs", self.total_times],
            ["Total Time", format_time(self.total_seconds_played)],
        ]

        display = tabulate(["Stat", "Value"], stats_rows, max_width=24) + "\n\n"

        return display

import json
import os

import pandas as pd
from bonusclasses.security import findpw, scramble, unscramble
from utils.enums import ExitCodes
from utils.general_utils import format_time, tabulate

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
]

# ! TODO: documentation


def decrypt(data_dict: dict[str, int], key: str) -> dict[str, int]:
    """Decrypt a dictionary of player data given a key.

    Args:
        data_dict (dict): The dictionary containing the player data
        key (str): The key used to decrypt the dictionary's contents

    Returns:
        A dict containing the decrypted entries of player data

    """
    return {k: unscramble(str(v), key) for k, v in data_dict.items()}


def encrypt(data_dict: dict[str, int], key: str) -> dict[str, int]:
    """Encrypt a dictionary of player data given a key.

    Args:
        data_dict (dict): The dictionary containing the player data
        key (str): The key used to encrypt the dictionary's contents

    Returns:
        A dict containing the encrypted entries of player data

    """
    return {k: scramble(str(v), key) for k, v in data_dict.items()}


# * Pandas helpers


def read_raw_rows() -> dict:
    """Read all player rows from Excel without decryption.
    
    Used for reading data in encrypted form.

    Returns:
        The raw data (no decryption) in the Excel file transcribed as dictionary.

    """
    df = pd.read_excel(EXCEL_FILE, engine="openpyxl")
    return df.to_dict(orient="records")


def read_all_rows() -> dict:
    """Read all player rows from Excel and decrypts all fields.

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
                pw = findpw(unencrypted_name, encrypted_name)
                decrypted = decrypt(
                    {k: str(v) for k, v in r.items() if k not in {"username", "encrypted_username"}},
                    pw,
                )
                decrypted["username"] = unencrypted_name
                decrypted["encrypted_username"] = encrypted_name
                r.update(decrypted)
            except KeyError as e:
                print(f"Failed to decrypt for {unencrypted_name}: {e}")

    return rows


def write_all_rows(rows: dict[str, int]) -> None:
    """Write all player rows (encrypted) back to Excel.

    Args:
        rows (dict): The encrypted rows

    """
    pd.DataFrame(rows, columns=HEADERS).to_excel(EXCEL_FILE, index=False, engine="openpyxl")


def safe_int(value: str | int | None) -> int:
    """Parse empty entries into integers if needed.

    Args:
        value (str | int | None): The value to be processed

    Returns:
        A processed integer for storage

    """
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return 0
    try:
        return int(value)
    except (ValueError, TypeError):
        return 0


def safe_float(value: str | float) -> float:
    """Parse empty entries into floats if needed.

    Args:
        value (str | float | None): The value to be processed

    Returns:
        A processed float for storage

    """
    if value is None or pd.isna(value):
        return 0
    try:
        return float(value)
    except (ValueError, TypeError):
        return 0


# * Actual Class Declaration


class PlayerData:
    """Handles the storing and sending of session data for each game session for a given player.

    Also handles distribution of global player information to leaderboards.

    Attributes:
        name (str): the name of the player
        password (str): the password of the player
        total_mushrooms_collected (int): the total mushrooms collected by the player
        total_tiles_walked (int): the total number of tiles a player walked throughout thegame.
        total_wins (int): the total wins a player had throughout the game.
        total_times (int): the total time the player has played
        total_seconds_played (int):  the total minimum time taken by a player to beat each of their completed levels
        completed_data (str): JSON containing data about levels a player has completed.
        completed_levels (dict): data about levels a player has completed.

    """

    def __init__(self, name: str, password: str | None = None) -> None:
        """Initialize the player's data storage given a name.

        Args:
            name (str): Denotes the name of the player
            password (str | None): Denotes the password of the player, to be used in decrypting

        """
        self.name = name
        self.password = password
        self.total_mushrooms_collected = 0
        self.total_tiles_walked = 0
        self.total_wins = 0
        self.total_times = 0
        self.total_seconds_played = 0
        self.reset_session()
        self.load_or_create()

    # * Log-In Validators

    @staticmethod
    def lookup_excel_username(username: str) -> str | None:
        """Return a username from the database if exists and None if does not.

        Args:
            username (str): The username to be accessed

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
    def store_new_user(username: str, encrypted_username: str) -> None:
        """Store a new username and initializes their data in the database if it does not exist in the database.

        Args:
            username (str): The username to store in the database.
            encrypted_username (str): The encrypted username to store (to find the key later).

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
        })
        write_all_rows(rows)

    # * Getter Methods
    def get_password(self) -> str:
        """Return the user's password.

        Returns:
            The player's password.

        """
        return self.password

    # * Setter Methods
    def set_password(self, key: str) -> None:
        """Set the password.

        Args:
            key (str): The given key.

        """
        self.password = key

    # * Session Setter Methods
    def reset_session(self) -> None:
        """Reset the session.

        Start time is recorded (to determine total length later).
        Win/dead conditions are set to false (as expected from any grid spawn).
        """
        self.session_mushrooms = 0
        self.session_tiles = 0
        self.session_win = False
        self.session_dead = False

    def record_move(self, n: int = 1) -> None:
        """Add number of moves to the session data.

        Args:
            n (int): The number of moves to be added

        """
        self.session_tiles += n

    def record_mushroom(self, n: int = 1) -> None:
        """Add number of mushrooms to the session data.

        Args:
            n (int): The number of mushrooms to be added

        """
        self.session_mushrooms += n

    def record_win(self) -> None:
        """Record a win for the player."""
        self.session_win = True

    def record_death(self) -> None:
        """Record a death for the player."""
        self.session_dead = True

    def load_or_create(self) -> None:
        """Reinitialize the player's statistics based on records in the database.

        This includes initializing the data for a new player.
        """
        rows = read_all_rows()
        for row in rows:
            if row["username"] == self.name:
                self.total_mushrooms_collected = safe_int(row.get("total_mushrooms_collected"))
                self.total_tiles_walked = safe_int(row.get("total_tiles_walked"))
                self.total_wins = safe_int(row.get("total_wins"))
                self.total_times = safe_int(row.get("total_times"))
                self.total_seconds_played = safe_float(row.get("total_seconds_played"))
                return

        raw_rows = read_raw_rows()
        raw_rows.append(self.to_dict())
        write_all_rows(raw_rows)

    # * Excel-Interaction Methods
    def commit_session(self) -> None:
        """Adjust the player data given a level file.

        Also logs the updated data to the database.
        """
        self.total_mushrooms_collected += self.session_mushrooms
        self.total_tiles_walked += self.session_tiles
        self.total_times += 1
        self.total_seconds_played += self.session_time
        if self.session_win:
            self.total_wins += 1
        self.save()
        self.reset_session()

    def save(self) -> None:
        """Save player data to the database."""
        rows = read_raw_rows()

        found = False
        for r in rows:
            if r["username"] == self.name:
                r.update(
                    self.to_dict(),
                )
                found = True
                break

        if not found:
            rows.append(self.to_dict())
        write_all_rows(rows)

    def to_dict(self) -> None:
        """Convert session data to a dict."""
        data = {
            "total_mushrooms_collected": self.total_mushrooms_collected,
            "total_tiles_walked": self.total_tiles_walked,
            "total_wins": self.total_wins,
            "total_times": self.total_times,
            "total_seconds_played": self.total_seconds_played,
        }
        if self.password:
            data = encrypt(data, self.password)
            data["encrypted_username"] = scramble(self.name, self.password)
        else:
            data["encrypted_username"] = self.name
        data["username"] = self.name
        return data

    def apply_report_dict(self, report: dict, return_code: ExitCodes | None = None, elapsed_time: float = 0) -> None:
        """Process the updates to be performed after receiving a session report.

        Args:
            report (dict): The latest session data
            return_code (ExitCodes | None): The exit code of the last game
            elapsed_time (float): The time taken for completion

        """
        self.session_mushrooms = safe_int(report["mushrooms_collected"])
        self.session_tiles = safe_int(report["moves_made"])
        self.session_time = elapsed_time
        self.session_win = report["win"]
        self.session_dead = report["dead"]

        if return_code in {ExitCodes.VICTORY.value, ExitCodes.DEFEAT.value}:
            if return_code == ExitCodes.VICTORY.value:
                self.record_win()
            self.commit_session()
            return

        self.commit_session()

    def load_report_file(self, path: str) -> None:
        """Load a report file.

        Args:
            path (str): The path to the report file

        """
        with open(path, encoding="utf-8") as f:
            report = json.load(f)
        return self.apply_report_dict(report)

    # * Display

    def __repr__(self) -> str:
        """Display the statistics belonging to a player in an organized manner.

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

        return tabulate(["Stat", "Value"], stats_rows) + "\n\n"

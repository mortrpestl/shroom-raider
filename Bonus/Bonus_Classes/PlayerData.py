from Utils.central_imports import *
from LevelManager import get_level_title
from .security import scramble, unscramble, findPW
import pandas as pd
import json
import os
import time

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
    "completed_data"
]

def decrypt(dict, key):
    return {k: unscramble(str(v),key) for k,v in dict.items()}

def encrypt(dict, key):
    return {k: scramble(str(v),key) for k,v in dict.items()}

# * Pandas helpers

def read_raw_rows():
    """
    Reads all player rows from Excel WITHOUT decryption.
    Use this when you need to preserve encrypted state.
    """
    df = pd.read_excel(EXCEL_FILE, engine="openpyxl")
    rows = df.to_dict(orient="records")
    
    for r in rows:
        cd = r.get("completed_data", "{}")
        if pd.isna(cd) or not cd or str(cd).strip().lower() == "nan":
            r["completed_data"] = "{}"
    
    return rows


def read_all_rows(): 
    """
    Reads all player rows from Excel and decrypts all fields.
    Use this ONLY for displaying/reading data, NOT for saving.
    """
    rows = read_raw_rows()

    for r in rows:
        # check if username is stored encrypted
        unencrypted_name = r.get("username")
        encrypted_name = r.get("encrypted_username")

        if unencrypted_name and encrypted_name and unencrypted_name != encrypted_name:
            try:
                pw = findPW(unencrypted_name, encrypted_name)
                decrypted = decrypt({k: str(v) for k, v in r.items() if k not in ("username", "encrypted_username")}, pw)
                decrypted["username"] = unencrypted_name
                decrypted["encrypted_username"] = encrypted_name
                r.update(decrypted)
            except Exception as e:
                print(f"Failed to decrypt for {unencrypted_name}: {e}")
    
    return rows


def write_all_rows(rows):
    pd.DataFrame(rows, columns=HEADERS).to_excel(
        EXCEL_FILE, index=False, engine="openpyxl"
    )


def safe_int(value):
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return 0
    try:
        return int(value)
    except (ValueError, TypeError):
        return 0


class PlayerData:
    def __init__(self, name, password=None):
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
    def lookup_excel_username(username):
        # Read decrypted rows for lookup
        rows = read_all_rows()
        for r in rows:
            if r["username"] == username:
                return r.get("encrypted_username"), r["username"]
        return None, username

    @staticmethod
    def store_new_user(username, encrypted_username):
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
            "completed_data": "{}"
        })
        write_all_rows(rows)

    # * Getter Methods
    def get_password(self):
        return self.password
    
    # * Setter Methods
    def set_password(self, key):
        self.password = key
    
    # * Session Setter Methods
    def reset_session(self):
        self.session_mushrooms = 0
        self.session_tiles = 0
        self.session_win = False
        self.session_dead = False
        self.session_start_time = time.time()

    def record_move(self, n=1):
        self.session_tiles += n

    def record_mushroom(self, n=1):
        self.session_mushrooms += n

    def record_win(self):
        self.session_win = True

    def record_death(self):
        self.session_dead = True

    def load_or_create(self):
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
        
        # User not found - need to create
        # Read RAW rows to preserve encryption of existing users
        raw_rows = read_raw_rows()
        raw_rows.append(self.to_dict())
        write_all_rows(raw_rows)

    # * Level Completion Handler Methods
    def get_completed_levels(self):
        if not self.completed_levels and self.completed_data:
            try:
                self.completed_levels = json.loads(self.completed_data)
            except Exception:
                self.completed_levels = {}
        return self.completed_levels

    def record_level_completion(self, level_id: int, elapsed_time_ms: int):
        completed = self.get_completed_levels()
        key = str(level_id)
        completed[key] = min(completed.get(key, elapsed_time_ms), elapsed_time_ms)
        self.completed_levels = completed
        self.completed_data = json.dumps(completed)

    # * Excel-Interaction Methods
    def commit_session(self, time_elapsed_ms: float):
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
        """
        Save player data to Excel, preserving encryption for all rows.
        Read RAW data to avoid double encryption.
        """
        # Read RAW Excel data WITHOUT decrypting
        rows = read_raw_rows()
        
        # Find and update our player's row
        found = False
        for r in rows:
            if r["username"] == self.name:
                r.update(self.to_dict())  # to_dict() handles encryption
                found = True
                break
        
        # If not found, append new row
        if not found:
            rows.append(self.to_dict())
    
        # Write back to Excel
        write_all_rows(rows)

    def to_dict(self):
        data = {
            "total_mushrooms_collected": self.total_mushrooms_collected,
            "total_tiles_walked": self.total_tiles_walked,
            "total_wins": self.total_wins,
            "total_times": self.total_times,
            "total_seconds_played": self.total_seconds_played,
            "completed_data": self.completed_data
        }
        if self.password:
            data = encrypt(data, self.password)
            data["encrypted_username"] = scramble(self.name, self.password)
        else:
            data["encrypted_username"] = self.name
        data["username"] = self.name
        return data

    def apply_report_dict(self, report, return_code=None, level_id=None, elapsed_time=0):
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
        with open(path, "r", encoding="utf-8") as f:
            report = json.load(f)
        return self.apply_report_dict(report, level_id=level_id)

    # * Display
    @debug_wait(WAIT_TIME)
    def __repr__(self):
        completed_levels = self.get_completed_levels()
        if not completed_levels:
            completed_rows = [["None"]]
            completed_headers = ["Completed Levels"]
        else:
            def sort_key(item):
                try:
                    folder, level = item[0].split("/")
                    return int(folder), int(level)
                except Exception:
                    return (0, 0)

            sorted_levels = sorted(completed_levels.items(), key=sort_key)
            completed_rows = [
                [level_id, get_level_title(*level_id.split('/')) or "-", format_time(ms)]
                for level_id, ms in sorted_levels
            ]
            completed_headers = ["ID", "Title", "Best Time"]

        stats_rows = [
            ["Player Name", self.name],
            ["Total Mushrooms", self.total_mushrooms_collected],
            ["Tiles Walked", self.total_tiles_walked],
            ["Total Wins", self.total_wins],
            ["Total Runs", self.total_times],
            ["Total Time", format_time(self.total_seconds_played)],
        ]

        tabulate(["Stat", "Value"], stats_rows, max_width=30)
        tabulate(completed_headers, completed_rows, max_width=30)

        return ""
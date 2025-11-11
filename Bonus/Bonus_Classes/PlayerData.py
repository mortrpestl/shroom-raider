import os
import json
import time
import pandas as pd

from Utils.exit_codes import EXIT_CODES
from Utils.general_utils import format_time, tabulate
from LevelManager import get_level_title

HERE = os.path.dirname(__file__)
EXCEL_FILE = os.path.abspath(os.path.join(HERE, "..", "Statistics", "PlayerData.xlsx"))
HEADERS = [
    "username",
    "total_mushrooms_collected",
    "total_tiles_walked",
    "total_wins",
    "total_times",
    "total_seconds_played",
    "completed_data",
]


# * Pandas helpers
def read_all_rows():
    df = pd.read_excel(EXCEL_FILE, engine="openpyxl")
    rows = df.to_dict(orient="records")
    for r in rows:
        cd = r.get("completed_data", "{}")
        if pd.isna(cd) or not cd or str(cd).strip().lower() == "nan":
            r["completed_data"] = "{}"
    return rows


def write_all_rows(rows):
    pd.DataFrame(rows, columns=HEADERS).to_excel(
        EXCEL_FILE, index=False, engine="openpyxl"
    )


def safe_int(value):
    # important, or we will run into errors with empty cells (from experience)
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return 0
    return int(value)


class Data:
    def __init__(self, name):
        self.name = name
        self.total_mushrooms_collected = 0
        self.total_tiles_walked = 0
        self.total_wins = 0
        self.total_times = 0
        self.total_seconds_played = 0
        self.completed_data = "{}"
        self.completed_levels = {}
        self.reset_session()
        self.load_or_create()

    # * Session Setter Methods
    def reset_session(self):
        self.session_mushrooms = 0
        self.session_tiles = 0
        self.session_win = False
        self.session_dead = False
        self.session_start_time = time.time()  # start timing this session

    def record_move(self, n=1):
        self.session_tiles += n

    def record_mushroom(self, n=1):
        self.session_mushrooms += n

    def record_win(self):
        self.session_win = True

    def record_death(self):
        self.session_dead = True

    def load_or_create(self):
        rows = read_all_rows()
        for row in rows:
            if row["username"] == self.name:
                self.total_mushrooms_collected = safe_int(
                    row.get("total_mushrooms_collected")
                )
                self.total_tiles_walked = safe_int(row.get("total_tiles_walked"))
                self.total_wins = safe_int(row.get("total_wins"))
                self.total_times = safe_int(row.get("total_times"))
                self.total_seconds_played = safe_int(row.get("total_seconds_played"))

                self.completed_data = (
                    row.get("completed_data", "{}") or "{}"
                )  # the {} is the create part
                try:
                    self.completed_levels = json.loads(self.completed_data)
                except Exception:
                    self.completed_levels = {}
                break
        else:
            rows.append(self.to_dict())
            write_all_rows(rows)

    # * Level Completion Handler Methods
    def get_completed_levels(self):
        if not self.completed_levels and self.completed_data:
            try:
                self.completed_levels = json.loads(self.completed_data)
            except Exception:
                self.completed_levels = {}
        return self.completed_levels

    def record_level_completion(self, level_id: int, elapsed_time_ms: int):
        # this only applies if you win
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
        rows = read_all_rows()
        for r in rows:
            if r["username"] == self.name:
                r.update(self.to_dict())
                break
        else:
            rows.append(self.to_dict())
        write_all_rows(rows)

    def to_dict(self):
        return {
            "username": self.name,
            "total_mushrooms_collected": self.total_mushrooms_collected,
            "total_tiles_walked": self.total_tiles_walked,
            "total_wins": self.total_wins,
            "total_times": self.total_times,
            "total_seconds_played": self.total_seconds_played,
            "completed_data": self.completed_data,
        }

    def apply_report_dict(
        self, report, return_code=None, level_id=None, elapsed_time=0
    ):
        # this updates regardless if you won, lost, or quit the game (aggregate stats)
        self.session_mushrooms = safe_int(report["mushrooms_collected"])
        self.session_tiles = safe_int(report["moves_made"])
        self.session_win = report["win"]
        self.session_dead = report["dead"]

        if self.session_win and level_id is not None:
            self.record_level_completion(level_id, elapsed_time)

        if return_code in (EXIT_CODES["victory"], EXIT_CODES["defeat"]):
            if return_code == EXIT_CODES["victory"]:
                self.record_win()
            self.commit_session(elapsed_time)
            return

        self.commit_session(elapsed_time)

    def load_report_file(self, path, level_id=None):
        with open(path, "r", encoding="utf-8") as f:
            report = json.load(f)
        return self.apply_report_dict(report, level_id=level_id)

    # * Display
    def __repr__(self):
        completed_levels = self.get_completed_levels()
        if not completed_levels:
            completed_rows = [["None"]]
            completed_headers = ["Completed Levels"]
        else:
            sorted_levels = sorted(completed_levels.items(), key=lambda x: int(x[0]))
            completed_rows = [
                [int(lvl_id), get_level_title(int(lvl_id)) or "-", format_time(ms)]
                for lvl_id, ms in sorted_levels
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

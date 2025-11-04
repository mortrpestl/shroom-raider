import os
import json
import pandas as pd

HERE = os.path.dirname(__file__)
EXCEL_FILE = os.path.abspath(os.path.join(HERE, "..", "Statistics", "PlayerData.xlsx"))
HEADERS = ["username","total_mushrooms_collected","total_tiles_walked","total_wins","total_times"]

# * Pandas helpers

def read_all_rows():
    df = pd.read_excel(EXCEL_FILE, dtype=str, engine="openpyxl")
    return df.to_dict(orient="records")

def write_all_rows(rows):
    pd.DataFrame(rows, columns=HEADERS).to_excel(EXCEL_FILE, index=False, engine="openpyxl")

def safe_int(value):
    return int(value)

class Data:
    def __init__(self, name):
        self.name = name
        self.total_mushrooms_collected = 0
        self.total_tiles_walked = 0
        self.total_wins = 0
        self.total_times = 0
        self.reset_session()
        self._load_or_create()


    # * Session Setter Methods

    def reset_session(self):
        self.session_mushrooms = 0
        self.session_tiles = 0
        self.session_win = False
        self.session_dead = False

    def record_move(self, n=1):
        self.session_tiles += n

    def record_mushroom(self, n=1):
        self.session_mushrooms += n

    def record_win(self):
        self.session_win = True

    def record_death(self):
        self.session_dead = True

    def _load_or_create(self):
        rows = read_all_rows()
        for row in rows:
            if row["username"] == self.name:
                self.total_mushrooms_collected = safe_int(row["total_mushrooms_collected"])
                self.total_tiles_walked = safe_int(row["total_tiles_walked"])
                self.total_wins = safe_int(row["total_wins"])
                self.total_times = safe_int(row["total_times"])
                break
        else:
            rows.append(self.to_dict())
            write_all_rows(rows)

    # * Excel-Interaction Methods
    
    def commit_session(self):
        self.total_mushrooms_collected += self.session_mushrooms
        self.total_tiles_walked += self.session_tiles
        self.total_times += 1
        if self.session_win:
            self.total_wins += 1
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
        }

    def apply_report_dict(self, report):
        self.session_mushrooms = safe_int(report["mushrooms_collected"])
        self.session_tiles = safe_int(report["moves_made"])
        self.session_win = report["win"]
        self.session_dead = report["dead"]
        self.commit_session()
        return True

    def load_report_file(self, path):
        with open(path, "r", encoding="utf-8") as f:
            report = json.load(f)
        return self.apply_report_dict(report)

    def __repr__(self):
        return f"""
+----------------------------------+
|  Player Name     : {self.name:<13} |
|  Total Mushrooms : {self.total_mushrooms_collected:<13} |
|  Tiles Walked    : {self.total_tiles_walked:<13} |
|  Total Wins      : {self.total_wins:<13} |
|  Total Runs      : {self.total_times:<13} |
+----------------------------------+
""".strip()
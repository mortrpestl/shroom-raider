import os
import pandas as pd
import openpyxl

EXCEL_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Statistics", "PlayerData.xlsx"))
HEADERS = [
    "username",
    "total_mushrooms_collected",
    "total_tiles_walked",
    "total_wins",
    "total_times", #can add more!
]

# * Helper Functions for Excel-Python data transfer

def read_all_rows():
    if not os.path.exists(EXCEL_FILE):
        pd.DataFrame(columns=HEADERS).to_excel(EXCEL_FILE, index=False, engine="openpyxl")
    df = pd.read_excel(EXCEL_FILE, dtype=str, engine="openpyxl")
    return df.fillna("").to_dict(orient="records")

def write_all_rows(rows):
    pd.DataFrame(rows, columns=HEADERS).to_excel(EXCEL_FILE, index=False, engine="openpyxl")

#convert empty cells to 0 (for safety)
def safe_int(value):
    try: return int(float(value))
    except (TypeError, ValueError): return 0

class Data:
    def __init__(self, name):
        self.name = name

        self.total_mushrooms_collected = 0
        self.total_tiles_walked = 0
        self.total_wins = 0
        self.total_times = 0

        #if there is data from Excel, load it
        rows = read_all_rows()
        for row in rows:
            if str(row.get("username")) == str(name):
                self.total_mushrooms_collected = safe_int(row.get("total_mushrooms_collected"))
                self.total_tiles_walked = safe_int(row.get("total_tiles_walked"))
                self.total_wins = safe_int(row.get("total_wins"))
                self.total_times = safe_int(row.get("total_times"))
                break
        else:
            rows.append(self.to_dict())
            write_all_rows(rows)

    #really important for debugging, may remove after
    def __repr__(self):
        return (
            f"Data(name={self.name!r}, mushrooms={self.total_mushrooms_collected}, "
            f"tiles={self.total_tiles_walked}, wins={self.total_wins}, times={self.total_times})"
        )

    def save(self):
        """
        Saves the current Data instance back to the PlayerData file.
        """
        rows = read_all_rows()
        for r in rows:
            if str(r.get("username")) == str(self.name):
                r.update({
                    "total_mushrooms_collected": self.total_mushrooms_collected,
                    "total_tiles_walked": self.total_tiles_walked,
                    "total_wins": self.total_wins,
                    "total_times": self.total_times,
                })
                break
        else: rows.append(self.to_dict())
        write_all_rows(rows)

    def to_dict(self):
        """
        Converts Data instance to dictionary.
        """
        return {
            "username": self.name,
            "total_mushrooms_collected": self.total_mushrooms_collected,
            "total_tiles_walked": self.total_tiles_walked,
            "total_wins": self.total_wins,
            "total_times": self.total_times,
        }

    def from_dict(self, data):
        """
        Converts dictionary (from Excel file) to Data instance.
        """
        inst = self(data.get("username"))
        inst.total_mushrooms_collected = safe_int(data.get("total_mushrooms_collected"))
        inst.total_tiles_walked = safe_int(data.get("total_tiles_walked"))
        inst.total_wins = safe_int(data.get("total_wins"))
        inst.total_times = safe_int(data.get("total_times"))
        return inst

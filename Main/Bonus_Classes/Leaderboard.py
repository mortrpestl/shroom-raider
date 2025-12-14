import json
import os

from Utils.general_utils import format_time, tabulate

from Bonus_Classes.PlayerData import read_all_rows

HERE = os.path.dirname(__file__)


# @debug_wait(WAIT_TIME)
def show_personal_leaderboard(pdata):
    """Shows completed levels, etc."""
    completed = pdata.get_completed_levels()
    if not completed:
        print("No completed levels yet.\n")
        return None

    rows = [
        [i + 1, get_level_title(*level_ref.split("/")) or "-", format_time(ms)]
        for i, (level_ref, ms) in enumerate(sorted(completed.items()))
    ]
    return tabulate(["#", "Title", "Best Time"], rows, max_width=24)


# @debug_wait(WAIT_TIME)
def show_general_leaderboard():
    """Compares player to other players. Ranked by levels beaten and sum of best times (formatted)"""
    players = read_all_rows()

    if not players:
        print("No leaderboard data available.\n")
        return None

    for p in players:
        try:
            completed = json.loads(p.get("completed_data", "{}"))
        except Exception:
            completed = {}

        # Sum of best times (in ms, then convert to formatted)
        total_ms = sum(completed.values())
        p["completed_levels"] = completed
        p["sum_best_ms"] = total_ms

    # Sort by levels completed, then by total ms (lower = better)
    players.sort(key=lambda p: (-len(p["completed_levels"]), p["sum_best_ms"]))

    rows = [
        [
            i + 1,
            p.get("username", ""),
            len(p.get("completed_levels", {})),
            format_time(p["sum_best_ms"]),
            p.get("total_mushrooms_collected", 0),
            p.get("total_tiles_walked", 0),
        ]
        for i, p in enumerate(players)
    ]

    headers = [
        "Rank",
        "Username",
        "Runs Played",
        "Sum of Best Times",
        "Mushrooms Collected",
        "Tiles Walked",
    ]
    return tabulate(headers, rows, max_width=24)


# @debug_wait(WAIT_TIME)
def show_level_leaderboard(level_ref):
    """Shows players who've beaten a level sorted by time."""
    players = read_all_rows()
    level_title = get_level_title(*level_ref.split("/")) or "UNTITLED"

    if not players:
        print(f"No player data for Level {level_ref} ({level_title}).\n")
        return None

    level_rows = []
    for p in players:
        try:
            completed = json.loads(p.get("completed_data", "{}"))
        except Exception:
            completed = {}
        if level_ref in completed:
            level_rows.append((p.get("username", ""), completed[level_ref]))

    if not level_rows:
        print(f"No completed times for Level {level_ref} ({level_title}).\n")
        return None

    level_rows.sort(key=lambda x: x[1])
    rows = [[i + 1, username, level_title, format_time(ms)] for i, (username, ms) in enumerate(level_rows)]
    return tabulate(["Rank", "Username", "Title", "Time"], rows, max_width=24)

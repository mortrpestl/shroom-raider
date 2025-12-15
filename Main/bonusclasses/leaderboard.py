import os

from bonusclasses.playerdata import read_all_rows
from utils.general_utils import calculate_percentage, format_time, tabulate

HERE = os.path.dirname(__file__)


def show_leaderboard(sort_by: str | tuple = "total_wins", reverse: bool = False) -> None:
    """Compares player to other players. Ranked by levels beaten and sum of best times (formatted)

    Args:
        sort_by (str | tuple): sorts the leaderboard using a key or a tuple of keys (by default, total_wins)
        reverse (bool): whether the leaderboard is sorted ascending or descending (by default, False)

    """
    players = read_all_rows()

    if not players:
        print("No leaderboard data available.\n")
        return

    if isinstance(sort_by, str):
        # sort by key
        players.sort(key=lambda p: p.get(sort_by), reverse=reverse)

    elif isinstance(sort_by, tuple):
        # sort by the first key then the next...
        players.sort(key=lambda p: tuple(p.get(i) for i in sort_by), reverse=reverse)

    rows = [
        [
            i + 1,
            p.get("username", ""),
            p.get("total_wins", 0),
            p.get("total_times", 0),
            calculate_percentage(int(p.get("total_wins", 0)), int(p.get("total_times", 0))),
            p.get("total_mushrooms_collected", 0),
            p.get("total_tiles_walked", 0),
            format_time(float(p.get("total_seconds_played", 0.0))),
        ]
        for i, p in enumerate(players)
    ]

    headers = [
        "Rank",
        "Username",
        "Total Wins",
        "Total Runs",
        "Win Accuracy",
        "Mushrooms Collected",
        "Tiles Walked",
        "Total Time Played",
    ]
    print(tabulate(headers, rows, max_width=24))

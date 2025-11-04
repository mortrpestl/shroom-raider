import os
import pandas as pd

HERE = os.path.dirname(__file__)
LEVELS_DIR = os.path.join(HERE, "Levels")
LEVELS_XLSX = os.path.join(LEVELS_DIR, "levels_list.xlsx")

def read_xlsx_levels():
    if not os.path.exists(LEVELS_XLSX):
        return []
    df = pd.read_excel(LEVELS_XLSX, engine="openpyxl")
    levels = []

    # expected columns: ID, Title, Description, Input Grid, Difficulty (case-insensitive)
    cols = {c.lower(): c for c in df.columns}
    id_col = cols.get("id")
    title_col = cols.get("title")
    desc_col = cols.get("description")
    grid_col = cols.get("input grid")
    diff_col = cols.get("difficulty")

    for _, row in df.iterrows():
        raw_grid = str(row[grid_col]) if grid_col and not pd.isna(row[grid_col]) else ""
        raw_grid = raw_grid.replace("\\n", "\n")

        difficulty = str(row[diff_col]).strip().title() if diff_col and not pd.isna(row[diff_col]) else "Normal"

        levels.append({
            "id": int(row[id_col]) if id_col and not pd.isna(row[id_col]) else None,
            "title": str(row[title_col]) if title_col and not pd.isna(row[title_col]) else "UNTITLED",
            "description": str(row[desc_col]) if desc_col and not pd.isna(row[desc_col]) else "",
            "difficulty": difficulty,
            "grid": raw_grid
        })
    return levels

def load_levels():
    """
    Returns a list of level dicts: {"id","title","description","difficulty","grid"}.
    """
    levels = read_xlsx_levels()
    for idx, lvl in enumerate(levels, 1):
        if lvl.get("id") is None:
            lvl["id"] = idx
    return levels

def list_level_titles(include_difficulty=False):
    """
    Returns [(id, title)] or [(id, title, difficulty)] depending on include_difficulty.
    """
    levels = load_levels()
    if include_difficulty:
        return [(lvl["id"], lvl["title"], lvl.get("difficulty", "Normal")) for lvl in levels]
    return [(lvl["id"], lvl["title"]) for lvl in levels]

def get_level_by_index(index):
    """
    index is 0-based index into load_levels() list.
    """
    levels = load_levels()
    if 0 <= index < len(levels):
        return levels[index]
    return None

def get_level_by_id(level_id):
    for lvl in load_levels():
        if lvl.get("id") == level_id:
            return lvl
    return None

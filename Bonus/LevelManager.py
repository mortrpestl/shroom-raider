import os
import pandas as pd

HERE = os.path.dirname(__file__)
LEVELS_DIR = os.path.join(HERE, "Levels")
LEVELS_XLSX = os.path.join(LEVELS_DIR, "levels_list.xlsx")


def read_xlsx_levels(folder_id: int):
    if not os.path.exists(LEVELS_XLSX):
        return []

    df = pd.read_excel(LEVELS_XLSX, engine="openpyxl", sheet_name=folder_id)
    levels = []

    # Expected columns: ID, Title, Description, Input Grid, Difficulty, Dark (case-insensitive)
    cols = {c.lower(): c for c in df.columns}
    id_col = cols.get("id")
    title_col = cols.get("title")
    desc_col = cols.get("description")
    grid_col = cols.get("input grid")
    diff_col = cols.get("difficulty")
    dark_col = cols.get("dark")

    for _, row in df.iterrows():
        raw_grid = (
            str(row[grid_col]).replace("\\n", "\n")
            if grid_col and not pd.isna(row[grid_col])
            else ""
        )

        difficulty = (
            str(row[diff_col]).strip().title()
            if diff_col and not pd.isna(row[diff_col])
            else "Normal"
        )

        # handle empty or missing dark radius
        dark_val = row[dark_col] if dark_col and not pd.isna(row[dark_col]) else None
        dark_radius = int(dark_val) if dark_val is not None else None

        levels.append(
            {
                "id": int(row[id_col]) if id_col and not pd.isna(row[id_col]) else None,
                "title": str(row[title_col]).strip()
                if title_col and not pd.isna(row[title_col])
                else "UNTITLED",
                "description": str(row[desc_col]).strip()
                if desc_col and not pd.isna(row[desc_col])
                else "",
                "difficulty": difficulty,
                "grid": raw_grid,
                "dark_radius": dark_radius,
            }
        )
    return levels

def read_xlsx_folders():
    if not os.path.exists(LEVELS_XLSX):
        return []

    df = pd.read_excel(LEVELS_XLSX, engine="openpyxl", sheet_name='Folders')
    folders = []

    # Expected columns: ID, Title, Description, Input Grid, Difficulty, Dark (case-insensitive)
    cols = {c.lower(): c for c in df.columns}
    id_col = cols.get("id")
    title_col = cols.get("title")
    desc_col = cols.get("description")

    for _, row in df.iterrows():
        folders.append(
            {
                "id": int(row[id_col]) if id_col and not pd.isna(row[id_col]) else None,
                "title": str(row[title_col]).strip()
                if title_col and not pd.isna(row[title_col])
                else "UNTITLED",
                "description": str(row[desc_col]).strip()
                if desc_col and not pd.isna(row[desc_col])
                else "",
            }
        )
    return folders

def load_levels(folder_id: int):
    """Returns a list of level dicts: {"id","title","description","difficulty","grid","dark_radius"}"""
    levels = read_xlsx_levels(folder_id)
    for idx, lvl in enumerate(levels, 1):
        if lvl.get("id") is None:
            lvl["id"] = idx
    return levels

def load_folders():
    folders = read_xlsx_folders()
    for idx, folder in enumerate(folders, 1):
        if folder.get("id") is None:
            folder['id'] = idx
        
    return folders


def get_level_by_id(folder_id: int, level_id: int):
    """Lookup a level by id."""

    for lvl in load_levels(folder_id):
        if lvl.get("id") == level_id:
            return lvl
    return None

def get_folder_by_id(folder_id: int):
    for folder in load_folders(folder_id):
        if folder.get('id') == folder_id:
            return folder
        
    return None

def get_folder_title(folder_id: int):
    folder = get_folder_by_id(folder_id)
    return folder['title'] if folder else None

def get_level_title(folder_id: int, level_id: int):
    """Return the title for a level id or None if not found."""
    lvl = get_level_by_id(int(folder_id), int(level_id))
    return lvl["title"] if lvl else None


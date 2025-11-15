import os
import pathlib

import pandas as pd
from Utils.general_utils import debug_wait

HERE = os.path.dirname(__file__)
LEVELS_DIR = os.path.join(HERE, "Levels")
LEVELS_XLSX = os.path.join(LEVELS_DIR, "levels_list.xlsx")

def read_xlsx_levels(folder_id: int):
    """Reads the levels in a given folder

    Args:
        folder_id: The number ID of the folder being accessed

    Returns:
        The levels in the folder, or an empty list if no levels exist

    """
    if not pathlib.Path(LEVELS_XLSX).exists():
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
    bee_col = cols.get("bee")
    bgm_col = cols.get("bgm")

    for _, row in df.iterrows():
        raw_grid = str(row.get(grid_col, "")).replace("\\n", "\n")
        difficulty = str(row.get(diff_col, "Normal")).strip().title()
        dark_val = row.get(dark_col)
        dark_radius = int(dark_val) if pd.notna(dark_val) else None
        bee_data = str(row.get(bee_col)) if bee_col and pd.notna(row.get(bee_col)) else None
        bgm_file = str(row.get(bgm_col)).strip() if bgm_col and pd.notna(row.get(bgm_col)) else "default-level-music.mp3"

        levels.append({
            "id": int(row[id_col]) if id_col and pd.notna(row.get(id_col)) else None,
            "title": str(row[title_col]).strip() if title_col and pd.notna(row.get(title_col)) else "UNTITLED",
            "description": str(row[desc_col]).strip() if desc_col and pd.notna(row.get(desc_col)) else "",
            "difficulty": difficulty,
            "grid": raw_grid,
            "dark_radius": dark_radius,
            "bee_data": bee_data,
            "bgm": bgm_file, 
        })

    return levels


def read_xlsx_folders():
    """Reads all folders that exist within the excel file

    Returns:
        A list of all the folders, or an empty list if there are no folders

    """
    if not pathlib.Path(LEVELS_XLSX).exists():
        return []

    df = pd.read_excel(LEVELS_XLSX, engine="openpyxl", sheet_name="Folders")
    folders = []

    cols = {c.lower(): c for c in df.columns}
    id_col = cols.get("id")
    title_col = cols.get("title")
    desc_col = cols.get("description")

    for _, row in df.iterrows():
        folders.append({
            "id": int(row[id_col]) if id_col and pd.notna(row.get(id_col)) else None,
            "title": str(row[title_col]).strip() if title_col and pd.notna(row.get(title_col)) else "UNTITLED",
            "description": str(row[desc_col]).strip() if desc_col and pd.notna(row.get(desc_col)) else "",
        })
    return folders


def load_levels(folder_id: int):
    """Loads the levels from the levels excel file

    Args:
        folder_id: The number ID of the folder bring accessed

    Returns:
        A list of all levels, with levels being represented as dictionaries of their level data


    """
    levels = read_xlsx_levels(folder_id)
    for idx, lvl in enumerate(levels, 1):
        if lvl.get("id") is None:
            lvl["id"] = idx
    return levels


def load_folders():
    """Loads the folders from the levels excel file

    Returns:
        A list of all folders, with folders being represented as dictionaries of their folder data

    """
    folders = read_xlsx_folders()
    for idx, folder in enumerate(folders, 1):
        if folder.get("id") is None:
            folder["id"] = idx

    return folders


def get_level_by_id(folder_id: int, level_id: int):
    """Lookup a level by id

    Args:
        folder_id: The ID of the folder being accessed
        level_id: The ID of the level being accessed

    Returns:
        The level if it exists, None if not

    """
    for lvl in load_levels(folder_id):
        if lvl.get("id") == level_id:
            return lvl
    return None


def get_folder_by_id(folder_id: int):
    """Lookup a folder by id

    Args:
        folder_id: The ID of the folder being accessed

    Returns:
        The folder if it exists, None if not

    """
    for folder in load_folders(folder_id):
        if folder.get("id") == folder_id:
            return folder

    return None


def get_folder_title(folder_id: int):
    """Gets the title of a given folder

    Args:
        folder_id: The ID of the folder being accessed

    Returns:
        The folder title if it exists, None if not

    """
    folder = get_folder_by_id(folder_id)
    return folder["title"] if folder else None


def get_level_title(folder_id: int, level_id: int):
    """Gets the title of a given folder

    Args:
        folder_id: The ID of the folder being accessed
        level_id: The ID of the level being accessed

    Returns:
        The level title if it exists, None if not

    """
    lvl = get_level_by_id(int(folder_id), int(level_id))
    return lvl["title"] if lvl else None

def get_folder_bgm_filename(folder_id: int):
    """Returns the BGM filename for a given folder from the Folders sheet.
    
    Args:
        folder_id: The ID of the folder being accessed

    Returns:
        The filename of the audio file associated with the folder
    """
    
    df = pd.read_excel(LEVELS_XLSX, sheet_name="Folders", engine="openpyxl")
    cols = {c.lower(): c for c in df.columns}
    id_col = cols.get("id")
    bgm_col = cols.get("bgm")

    row = df[df[id_col] == folder_id]
    if row.empty or bgm_col is None:
        return "default-level-music.mp3"

    bgm_value = row[bgm_col].iloc[0]
    if pd.isna(bgm_value):
        return "default-level-music.mp3"

    return str(bgm_value).strip()

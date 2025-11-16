import os
import pathlib

import pandas as pd

HERE = os.path.dirname(__file__)
LEVELS_DIR = os.path.join(HERE, "Levels")
LEVELS_XLSX = os.path.join(LEVELS_DIR, "levels_list.xlsx")

def valid_col(row, col):
    return col and pd.notna(row.get(col))

def clean_str(string):
    return str(string).strip()
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
    bgm_title_col = cols.get("song name")

    for _, row in df.iterrows():
        id = int(row[id_col]) if valid_col(row, id_col) else None
        title = clean_str(row[title_col]) if valid_col(row, title_col) else "UNTITLED"
        description = clean_str(row[desc_col]) if valid_col(row, desc_col) else ""
        raw_grid = clean_str(row.get(grid_col, "")).replace("\\n", "\n")
        difficulty = clean_str(row.get(diff_col, "Normal"))
        dark_val = row.get(dark_col)
        dark_radius = int(dark_val) if pd.notna(dark_val) else None
        bee_data = clean_str(row.get(bee_col)) if valid_col(row, bee_col) else None
        bgm_file = clean_str(row.get(bgm_col)) if valid_col(row, bgm_col) else "default-level-music.mp3"
        bgm_title = clean_str(row.get(bgm_title_col)) if valid_col(row, bgm_title_col) else "Box Has Key - Baba is You OST"

        levels.append({
            "id": id,
            "title": title,
            "description": description,
            "difficulty": difficulty,
            "grid": raw_grid,
            "dark_radius": dark_radius,
            "bee_data": bee_data,
            "bgm": bgm_file, 
            "song_name": bgm_title,
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
    song_col = cols.get("song name")

    for _, row in df.iterrows():
        folders.append({
            "id": int(row[id_col]) if valid_col(row,id_col) else None,
            "title": clean_str(row[title_col]) if valid_col(row,title_col) else "UNTITLED",
            "description": clean_str(row[desc_col]) if valid_col(row,desc_col) else "",
            "song_name": clean_str(row[song_col]) if valid_col(row,song_col) else "Baba Is You OST - Baba Is You Theme"
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

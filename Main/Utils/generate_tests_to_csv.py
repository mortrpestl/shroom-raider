from pathlib import Path

import pandas as pd

base_dir = Path(__file__).resolve().parent

excel_path = base_dir / "shroom-raider-tests-jugemu-jugemu.xlsx"
logs_dir = (base_dir / ".." / ".." / "Logs").resolve()

df = pd.read_excel(excel_path, dtype=str)
df["ID"] = df["ID"].astype(str)


def read_if_exists(folder_path: Path, filename: str) -> str:
    path = folder_path / filename
    if path.exists():
        return path.read_text(encoding="utf-8").strip()
    return ""


for folder in logs_dir.iterdir():
    if not folder.is_dir() or not folder.name.isdigit():
        continue
    id_str = folder.name

    map_txt = read_if_exists(folder, "map.txt")
    input_txt = read_if_exists(folder, "input.txt")
    output_txt = read_if_exists(folder, "output.txt")

    mask = df["ID"] == id_str
    if mask.any():
        df.loc[mask, "Input Grid"] = map_txt
        df.loc[mask, "Input String"] = input_txt
        df.loc[mask, "Output"] = output_txt
    else:
        print(f"Warning: Folder {folder.name} has no matching ID in Excel.")

output_file = base_dir / "unit_tests.xlsx"
df.to_excel(output_file, index=False, engine="openpyxl")

print(f"Merged data saved to: {output_file}")

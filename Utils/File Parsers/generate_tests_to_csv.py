import os
import pandas as pd

base_dir = os.path.dirname(os.path.abspath(__file__))

excel_path = os.path.join(base_dir, "shroom-raider-tests-jugemu-jugemu.xlsx")

logs_dir = os.path.join(base_dir, "..","..","Logs")
logs_dir = os.path.abspath(logs_dir)

df = pd.read_excel(excel_path,dtype=str)
df["ID"] = df["ID"].astype(str)

for folder in os.listdir(logs_dir):
    if not folder.isdigit():
        continue
    folder_path = os.path.join(logs_dir, folder)
    id_str = str(folder)

    def read_if_exists(filename):
        path = os.path.join(folder_path, filename)
        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                return f.read().strip()
        return ""

    map_txt = read_if_exists("map.txt")
    input_txt = read_if_exists("input.txt")
    output_txt = read_if_exists("output.txt")

    mask = df["ID"] == id_str
    if mask.any():
        df.loc[mask, "Input Grid"] = map_txt
        df.loc[mask, "Input String"] = input_txt
        df.loc[mask, "Output"] = output_txt
    else:
        print(f"Warning: Folder {folder} has no matching ID in Excel.")

output_file = os.path.join(base_dir, "unit_tests.xlsx")
df.to_excel(output_file, index=False, engine="openpyxl")

print(f"Merged data saved to: {output_file}")

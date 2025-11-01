import os
import subprocess
import tempfile
import pandas as pd
import pytest
import shutil

base_dir = os.path.dirname(os.path.abspath(__file__))
TEMP_DIR = os.path.join(base_dir, "Temp")
os.makedirs(TEMP_DIR, exist_ok=True)

EXCEL_FILE = os.path.join(base_dir, "integrated_tests.xlsx")
SCRIPT = os.path.join(base_dir, "..", "..", "shroom_raider.py")

#delete all files/folders generated after Integrated Tests
@pytest.fixture(scope="session", autouse=True)
def cleanup_unit_tests():
    yield
    if os.path.exists(TEMP_DIR):
        shutil.rmtree(TEMP_DIR)

"""
Integrated Testing

- use this if you want to test input/expected output comparison
- open the integrated_tests.xlsx folder and add expected input/output

"""



# read and extract rows from excel file
df = pd.read_excel(EXCEL_FILE, dtype=str)
df.columns = [c if not c.startswith("Unnamed") else "Category" for c in df.columns]
df.fillna("", inplace=True)

required = {"Category", "ID", "Description", "Input Grid", "Input String", "Output"}
missing = required - set(df.columns)
if missing: raise ValueError(f"Missing columns in Excel file: {missing}")

def extract_short_date(date_val):
    try:
        dt = pd.to_datetime(date_val, errors='coerce')
        if pd.isna(dt): return ""
        return dt.strftime("%y-%m-%d")
    except Exception:
        return ""

df["Day Added"] = df["Date Added"].apply(extract_short_date)

def run_game_case(testcase):
    test_id = testcase["ID"]
    category = testcase["Category"]
    desc = testcase["Description"].strip()
    date = testcase.get("Day Added", "").strip()
    grid_raw = testcase["Input Grid"].replace('\r\n', '\n').replace('\r', '\n').strip()
    moves_raw = testcase["Input String"].replace('\r\n', '\n').replace('\r', '\n').rstrip("\n")
    expected_output = testcase["Output"].replace('\r\n', '\n').replace('\r', '\n').strip()

    if not grid_raw:
        pytest.skip(f"{test_id} No grid provided.")
    if not expected_output:
        pytest.skip(f"{test_id} No expected output.")

    levels_dir = os.path.join(TEMP_DIR, "Levels")
    os.makedirs(levels_dir, exist_ok=True)
    level_path = os.path.join(levels_dir, f"test_{test_id}.txt")

    lines = grid_raw.splitlines()
    header_present = False
    if lines:
        first_parts = lines[0].strip().split()
        if len(first_parts) == 2 and all(p.isdigit() for p in first_parts):
            header_present = True

    with open(level_path, "w", encoding="utf-8") as f:
        if header_present:
            f.write("\n".join(lines))
        else:
            r = len(lines)
            c = len(lines[0])
            f.write(f"{r} {c}\n")
            f.write("\n".join(lines))

    tmp_out_path = os.path.join(TEMP_DIR, f"out_{test_id}.txt")
    env = {**os.environ, "PYTHONIOENCODING": "utf-8"}

    proc = subprocess.run(
        ["python3", SCRIPT, "-f", level_path, "-m", moves_raw, "-o", tmp_out_path],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="ignore",
        env=env,
        timeout=30,
    )

    if proc.returncode != 0:
        raise AssertionError(
            f"Script crashed for test {test_id} ({category})\n"
            f"stderr:\n{proc.stderr}\n"
            f"stdout:\n{proc.stdout}"
        )

    if not os.path.exists(tmp_out_path):
        raise AssertionError(f"Expected output file not created by script for test {test_id}")

    with open(tmp_out_path, "r", encoding="utf-8", errors="ignore") as f:
        actual_output = f.read().strip()

    os.remove(tmp_out_path)
    os.remove(level_path)
    
    return expected_output, actual_output, desc, date, category

#this is where the fun begins
params = [
    pytest.param(tc, id=f"Integrated Test {tc['ID'].zfill(3)} | {tc['Category'][:24]:^24} | {tc['Description']:<90}")
    for tc in df.to_dict("records")
]

#if you desire a date feature
# params = [
#     pytest.param(tc, id=f"Integrated Test {tc['ID'].zfill(3)} | {tc['Category'][:12]:^24} | {tc['Description'][:50]:^50} | {tc.get('Day Added','')[:8]:^8}")
#     for tc in df.to_dict("records")
# ]

#generate tests for each assert
@pytest.mark.parametrize("testcase", params)
def test_shroom_case(testcase):
    expected, actual, desc, date, category = run_game_case(testcase)
    test_id = testcase["ID"]
    moves = testcase["Input String"]

    if actual != expected:
        expected_lines = expected.splitlines()
        actual_lines = actual.splitlines()
        max_lines = max(len(expected_lines), len(actual_lines))

        max_line_no_width = len(str(max_lines))
        line_header = f"{'Line':^{max_line_no_width}} | {'Expected':^40} | {'Got':^40}"
        comparison = [line_header]
        comparison.append("-" * (max_line_no_width + 3 + 40 + 3 + 40))

        for i in range(max_lines):
            exp = expected_lines[i] if i < len(expected_lines) else ""
            act = actual_lines[i] if i < len(actual_lines) else ""
            comparison.append(f"{str(i+1):^{max_line_no_width}} | {exp:^40} | {act:^40}")

        pretty_output = "\n".join(comparison)
        raise AssertionError(
            f"\n🤔😔 Test failed! 🤣😂\n"
            f"Category: {category}\n"
            f"ID: {test_id}\n"
            f"Test Case Added at Date: {date}\n"
            f"Description: {desc}\n"
            f"Moves:\n{moves}\n\n"
            f"\n{pretty_output}\n")

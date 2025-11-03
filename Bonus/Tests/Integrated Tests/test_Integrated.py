import os
import subprocess
import tempfile
import pandas as pd
import pytest
import shutil

# Base directory of this test file
base_dir = os.path.dirname(os.path.abspath(__file__))

# Temporary directory for test outputs
TEMP_DIR = os.path.join(base_dir, "Temp")
os.makedirs(TEMP_DIR, exist_ok=True)

# Paths for input Excel test cases and the main game script
EXCEL_FILE = os.path.join(base_dir, "integrated_tests.xlsx")
SCRIPT = os.path.join(base_dir, "..", "..", "shroom_raider.py")


@pytest.fixture(scope="session", autouse=True)
def cleanup_unit_tests():
    """Fixture that cleans up temporary files and directories after all tests."""
    yield
    if os.path.exists(TEMP_DIR):
        shutil.rmtree(TEMP_DIR)

"""
Integrated Testing

- File eads test cases from an Excel sheet, runs the game script with the provided input,
  and compares the output to the expected output.
- For testing actual game logic.
- Add test cases in the 'integrated_tests.xlsx' file, and run 'pytest -v' to see it all run.
"""

# Read test cases from Excel and normalize columns
df = pd.read_excel(EXCEL_FILE, dtype=str)
df.columns = [c if not c.startswith("Unnamed") else "Category" for c in df.columns]
df.fillna("", inplace=True)

# Ensure required columns exist in the Excel sheet
required = {"Category", "ID", "Description", "Input Grid", "Input String", "Output"}
missing = required - set(df.columns)
if missing: raise ValueError(f"Missing columns in Excel file: {missing}")


def extract_short_date(date_val):
    """
    Convert a date string to a short 'YY-MM-DD' format.

    Returns an empty string if the conversion fails or the value is invalid.
    """
    try:
        dt = pd.to_datetime(date_val, errors='coerce')
        if pd.isna(dt): return ""
        return dt.strftime("%y-%m-%d")
    except Exception:
        return ""


# Add a 'Day Added' column with formatted dates
df["Day Added"] = df["Date Added"].apply(extract_short_date)


def run_game_case(testcase):
    """
    Execute the game for a single test case.

    - Writes the grid to a temporary file
    - Runs the game script with the input moves
    - Captures the script's output
    - Cleans up temporary files
    Returns: expected_output, actual_output, description, date, category
    """
    test_id = testcase["ID"]
    category = testcase["Category"]
    desc = testcase["Description"].strip()
    date = testcase.get("Day Added", "").strip()
    grid_raw = testcase["Input Grid"].replace('\r\n', '\n').replace('\r', '\n').strip()
    moves_raw = testcase["Input String"].replace('\r\n', '\n').replace('\r', '\n').rstrip("\n")
    expected_output = testcase["Output"].replace('\r\n', '\n').replace('\r', '\n').strip()

    # Skip if input grid or expected output is missing
    if not grid_raw:
        pytest.skip(f"{test_id} No grid provided.")
    if not expected_output:
        pytest.skip(f"{test_id} No expected output.")

    # Prepare temporary level file
    levels_dir = os.path.join(TEMP_DIR, "Levels")
    os.makedirs(levels_dir, exist_ok=True)
    level_path = os.path.join(levels_dir, f"test_{test_id}.txt")

    lines = grid_raw.splitlines()
    header_present = False
    if lines:
        first_parts = lines[0].strip().split()
        if len(first_parts) == 2 and all(p.isdigit() for p in first_parts):
            header_present = True

    # Write the grid to the temporary file
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

    # Run the game script
    proc = subprocess.run(
        ["python3", SCRIPT, "-f", level_path, "-m", moves_raw, "-o", tmp_out_path],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="ignore",
        env=env,
        timeout=30,
    )

    # Raise error if script crashes
    if proc.returncode != 0:
        raise AssertionError(
            f"Script crashed for test {test_id} ({category})\n"
            f"stderr:\n{proc.stderr}\n"
            f"stdout:\n{proc.stdout}"
        )

    # Raise error if output file is not created
    if not os.path.exists(tmp_out_path):
        raise AssertionError(f"Expected output file not created by script for test {test_id}")

    # Read the output
    with open(tmp_out_path, "r", encoding="utf-8", errors="ignore") as f:
        actual_output = f.read().strip()

    # Clean up temporary files
    os.remove(tmp_out_path)
    os.remove(level_path)
    
    return expected_output, actual_output, desc, date, category


# Generate pytest parameters with readable test IDs
params = [
    pytest.param(
        tc,
        id=f"Integrated Test {tc['ID'].zfill(3)} | {tc['Category'][:24]:^24} | {tc['Description']:<90}"
    )
    for tc in df.to_dict("records")
]

# Uncomment if you want to include the date in test IDs
# params = [
#     pytest.param(tc, id=f"Integrated Test {tc['ID'].zfill(3)} | {tc['Category'][:12]:^24} | {tc['Description'][:50]:^50} | {tc.get('Day Added','')[:8]:^8}")
#     for tc in df.to_dict("records")
# ]

@pytest.mark.parametrize("testcase", params)
def test_shroom_case(testcase):
    """
    Run a single integrated test case.

    - Compares the actual output to the expected output line by line
    - Raises an assertion error if outputs differ, with a formatted comparison table
    """
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

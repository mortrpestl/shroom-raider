#!/usr/bin/env python3
from __future__ import annotations

import os
import shutil
import subprocess  # noqa: S404
import sys
from pathlib import Path

import pandas as pd
import pytest

# Base directory of this test file
base_dir = Path(__file__).resolve().parent

# Temporary directory for test outputs
TEMP_DIR = base_dir / "Temp"
TEMP_DIR.mkdir(exist_ok=True, parents=True)

# Paths for input Excel test cases and the main game script
EXCEL_FILE = base_dir / "integrated_tests.xlsx"
SCRIPT = (base_dir / ".." / ".." / "shroom_raider.py").resolve()


@pytest.fixture(scope="session", autouse=True)
def cleanup_unit_tests() -> None:
    """Fixture that cleans up temporary files and directories after all tests.

    Yields:
        None

    """
    yield
    if TEMP_DIR.exists():
        shutil.rmtree(TEMP_DIR)


"""
Integrated Testing

- File reads test cases from an Excel sheet, runs the game script with the provided input,
  and compares the output to the expected output.
- For testing actual game logic.
- Add test cases in the 'integrated_tests.xlsx' file, and run 'pytest -v' to see it all run.
"""

# Read test cases from Excel and normalize columns
df = pd.read_excel(EXCEL_FILE, dtype=str)
df.columns = [c if not c.startswith("Unnamed") else "Category" for c in df.columns]
df = df.fillna("")

# Ensure required columns exist in the Excel sheet
required = {"Category", "ID", "Description", "Input Grid", "Input String", "Output"}
missing = required - set(df.columns)
if missing:
    raise ValueError(f"Missing columns in Excel file: {missing}")


def extract_short_date(date_val: object) -> str:
    """Convert a date string to a short 'YY-MM-DD' format.

    Returns:
        A short date string (YY-MM-DD) or empty string if invalid.

    """
    try:
        dt = pd.to_datetime(date_val, errors="coerce")
        if pd.isna(dt):
            return ""
        return dt.strftime("%y-%m-%d")
    except (ValueError, TypeError):
        return ""


# Add a 'Day Added' column with formatted dates
df["Day Added"] = df.get("Date Added", "").apply(extract_short_date)


def _write_level_file(test_id: str, grid_raw: str) -> Path:
    """Write `grid_raw` to a temporary level file and return its Path.

    Returns:
        Path to written temporary level file.

    """
    levels_dir = TEMP_DIR / "Levels"
    levels_dir.mkdir(exist_ok=True, parents=True)
    level_path = levels_dir / f"test_{test_id}.txt"

    lines = grid_raw.splitlines()
    header_present = False
    if lines:
        first_parts = lines[0].strip().split()
        if len(first_parts) == 2 and all(p.isdigit() for p in first_parts):
            header_present = True

    with level_path.open("w", encoding="utf-8") as f:
        if header_present:
            f.write("\n".join(lines))
        else:
            r = len(lines)
            c = len(lines[0]) if lines else 0
            f.write(f"{r} {c}\n")
            f.write("\n".join(lines))

    return level_path


def run_game_case(testcase: dict[str, str]) -> tuple[str, str, str, str, str]:
    """Execute the game for a single test case.

    - Writes the grid to a temporary file
    - Runs the game script with the input moves
    - Captures the script's output
    - Cleans up temporary files

    Returns:
        expected_output, actual_output, description, date, category

    Raises:
        AssertionError: If the script crashes or expected output file is not produced.

    """
    test_id = testcase["ID"]
    category = testcase["Category"]
    desc = testcase["Description"].strip()
    date = testcase.get("Day Added", "").strip()
    grid_raw = testcase["Input Grid"].replace("\r\n", "\n").replace("\r", "\n").strip()
    moves_raw = testcase["Input String"].replace("\r\n", "\n").replace("\r", "\n").rstrip("\n")
    expected_output = testcase["Output"].replace("\r\n", "\n").replace("\r", "\n").strip()

    # Skip if input grid or expected output is missing
    if not grid_raw:
        pytest.skip(f"{test_id} No grid provided.")
    if not expected_output:
        pytest.skip(f"{test_id} No expected output.")

    level_path = _write_level_file(test_id, grid_raw)
    tmp_out_path = TEMP_DIR / f"out_{test_id}.txt"

    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"

    # Run the game script using the same Python interpreter
    proc = subprocess.run(  # noqa: S603
        [sys.executable, str(SCRIPT), "-f", str(level_path), "-m", moves_raw, "-o", str(tmp_out_path)],
        check=False,
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
            f"Script crashed for test {test_id} ({category})\nstderr:\n{proc.stderr}\nstdout:\n{proc.stdout}",
        )

    # Raise error if output file is not created
    if not tmp_out_path.exists():
        raise AssertionError(f"Expected output file not created by script for test {test_id}")

    # Read the output
    actual_output = tmp_out_path.read_text(encoding="utf-8", errors="ignore")

    # Clean up temporary files
    tmp_out_path.unlink(missing_ok=True)
    level_path.unlink(missing_ok=True)

    return expected_output, actual_output, desc, date, category


def _format_diff(expected: str, actual: str) -> str:
    """Create a pretty diff table for expected vs actual strings.

    Returns:
        Better formatted assert

    """
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
        comparison.append(f"{i + 1!s:^{max_line_no_width}} | {exp:^40} | {act:^40}")

    return "\n".join(comparison)


# Generate pytest parameters with readable test IDs
params = [
    pytest.param(
        tc,
        id=f"Integrated Test {tc['ID'].zfill(3)} | {tc['Category'][:24]:^24} | {tc['Description']:<90}",
    )
    for tc in df.to_dict("records")
]


@pytest.mark.parametrize("testcase", params)
def test_shroom_case(testcase: dict[str, str]) -> None:
    """Run a single integrated test case.

    - Compares the actual output to the expected output line by line.
    - Raises an AssertionError if outputs differ.
    """
    expected, actual, desc, date, category = run_game_case(testcase)
    test_id = testcase["ID"]
    moves = testcase["Input String"]

    assert actual == expected, (
        f"\n🤔😔 Test failed! 🤣😂\n"
        f"Category: {category}\n"
        f"ID: {test_id}\n"
        f"Test Case Added at Date: {date}\n"
        f"Description: {desc}\n"
        f"Moves:\n{moves}\n\n"
        f"{_format_diff(expected, actual)}"
    )

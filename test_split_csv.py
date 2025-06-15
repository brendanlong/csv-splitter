#!/usr/bin/env python3
"""Tests for the CSV splitter script."""

import csv
import subprocess
import sys
from pathlib import Path
from typing import List

import pytest


@pytest.fixture
def temp_dir(tmp_path: Path) -> Path:
    """Create a temporary directory for test files."""
    return tmp_path


def create_csv_file(path: Path, headers: List[str], rows: List[List[str]]) -> None:
    """Create a CSV file with given headers and rows."""
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)


def read_csv_file(path: Path) -> tuple[List[str], List[List[str]]]:
    """Read a CSV file and return headers and rows."""
    with open(path, "r", newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        headers = next(reader)
        rows = list(reader)
    return headers, rows


def run_split_csv(input_file: Path, max_lines: int) -> subprocess.CompletedProcess[str]:
    """Run the split_csv.py script with given arguments."""
    script_path = Path(__file__).parent / "split_csv.py"
    return subprocess.run(
        [
            sys.executable,
            str(script_path),
            "--input-csv",
            str(input_file),
            "--max-lines",
            str(max_lines),
        ],
        capture_output=True,
        text=True,
    )


def test_split_file_with_just_header(temp_dir: Path) -> None:
    """Test splitting a file that contains only a header row."""
    input_file = temp_dir / "header_only.csv"
    headers = ["Name", "Age", "City"]
    create_csv_file(input_file, headers, [])

    result = run_split_csv(input_file, 5)

    assert result.returncode == 0
    assert "No data rows found in the input file" in result.stdout

    # List all files in directory
    all_files = sorted([f.name for f in temp_dir.iterdir()])
    assert all_files == ["header_only.csv"]  # Only the input file should exist


def test_split_empty_file(temp_dir: Path) -> None:
    """Test splitting an empty file (should show error)."""
    input_file = temp_dir / "empty.csv"
    input_file.write_text("")

    result = run_split_csv(input_file, 5)

    assert result.returncode == 0
    assert "Error: Input file is empty" in result.stdout

    # List all files in directory
    all_files = sorted([f.name for f in temp_dir.iterdir()])
    assert all_files == ["empty.csv"]  # Only the input file should exist


def test_split_file_with_exactly_max_lines(temp_dir: Path) -> None:
    """Test splitting a file with exactly max-lines rows."""
    input_file = temp_dir / "exact.csv"
    headers = ["ID", "Name", "Value"]
    rows = [[str(i), f"Name{i}", f"Value{i}"] for i in range(1, 6)]  # 5 rows
    create_csv_file(input_file, headers, rows)

    result = run_split_csv(input_file, 5)

    assert result.returncode == 0
    assert "Created: " in result.stdout
    assert "Split complete: Created 1 files" in result.stdout

    # List all files in directory
    all_files = sorted([f.name for f in temp_dir.iterdir()])
    assert all_files == ["exact.1-5.csv", "exact.csv"]

    # Check the output file
    output_file = temp_dir / "exact.1-5.csv"
    out_headers, out_rows = read_csv_file(output_file)
    assert out_headers == headers
    assert out_rows == rows


def test_split_file_larger_than_max_lines(temp_dir: Path) -> None:
    """Test splitting a file with more rows than max-lines."""
    input_file = temp_dir / "large.csv"
    headers = ["ID", "Name", "Value"]
    rows = [[str(i), f"Name{i}", f"Value{i}"] for i in range(1, 16)]  # 15 rows
    create_csv_file(input_file, headers, rows)

    result = run_split_csv(input_file, 5)

    assert result.returncode == 0
    assert "Split complete: Created 3 files" in result.stdout

    # List all files in directory
    all_files = sorted([f.name for f in temp_dir.iterdir()])
    assert all_files == [
        "large.1-5.csv",
        "large.11-15.csv",
        "large.6-10.csv",
        "large.csv",
    ]

    # Check first file (rows 1-5)
    out_headers, out_rows = read_csv_file(temp_dir / "large.1-5.csv")
    assert out_headers == headers
    assert out_rows == rows[0:5]

    # Check second file (rows 6-10)
    out_headers, out_rows = read_csv_file(temp_dir / "large.6-10.csv")
    assert out_headers == headers
    assert out_rows == rows[5:10]

    # Check third file (rows 11-15)
    out_headers, out_rows = read_csv_file(temp_dir / "large.11-15.csv")
    assert out_headers == headers
    assert out_rows == rows[10:15]


def test_split_file_not_evenly_divisible(temp_dir: Path) -> None:
    """Test splitting a file where row count is not evenly divisible by max-lines."""
    input_file = temp_dir / "uneven.csv"
    headers = ["ID", "Name", "Value"]
    rows = [[str(i), f"Name{i}", f"Value{i}"] for i in range(1, 13)]  # 12 rows
    create_csv_file(input_file, headers, rows)

    result = run_split_csv(input_file, 5)

    assert result.returncode == 0
    assert "Split complete: Created 3 files" in result.stdout

    # List all files in directory
    all_files = sorted([f.name for f in temp_dir.iterdir()])
    assert all_files == [
        "uneven.1-5.csv",
        "uneven.11-12.csv",
        "uneven.6-10.csv",
        "uneven.csv",
    ]

    # Check third file (rows 11-12) - should have only 2 rows
    out_headers, out_rows = read_csv_file(temp_dir / "uneven.11-12.csv")
    assert out_headers == headers
    assert out_rows == rows[10:12]


def test_invalid_max_lines(temp_dir: Path) -> None:
    """Test with invalid max-lines values."""
    input_file = temp_dir / "test.csv"
    headers = ["A", "B"]
    create_csv_file(input_file, headers, [["1", "2"]])

    # Test with zero
    result = run_split_csv(input_file, 0)
    assert result.returncode == 0
    assert "Error: --max-lines must be a positive integer" in result.stdout

    # Test with negative number
    result = run_split_csv(input_file, -5)
    assert result.returncode == 0
    assert "Error: --max-lines must be a positive integer" in result.stdout


def test_nonexistent_input_file(temp_dir: Path) -> None:
    """Test with a nonexistent input file."""
    input_file = temp_dir / "nonexistent.csv"

    result = run_split_csv(input_file, 5)

    assert result.returncode == 0
    assert "Error: Input file" in result.stdout
    assert "does not exist" in result.stdout

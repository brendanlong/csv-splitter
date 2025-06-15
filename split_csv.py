#!/usr/bin/env python3
"""Split a CSV file into multiple files with a maximum number of lines each."""

import argparse
import csv
from pathlib import Path
from typing import List


def split_csv(input_file: Path, max_lines: int) -> None:
    """Split a CSV file into multiple files with max_lines rows each.

    Args:
        input_file: Path to the input CSV file
        max_lines: Maximum number of data rows per output file (excluding header)
    """
    # Read the header first
    with open(input_file, "r", newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        try:
            header = next(reader)
        except StopIteration:
            print("Error: Input file is empty")
            return

        # Get the base name without extension
        base_name = input_file.stem
        extension = input_file.suffix
        output_dir = input_file.parent

        # Process the rest of the file in chunks
        chunk_num = 0
        row_num = 1  # Start from 1 (header is row 0)

        while True:
            # Collect up to max_lines rows
            chunk: List[List[str]] = []
            start_row = row_num

            for _ in range(max_lines):
                try:
                    row = next(reader)
                    chunk.append(row)
                    row_num += 1
                except StopIteration:
                    break

            if not chunk:
                break

            # Calculate end row (inclusive)
            end_row = row_num - 1

            # Create output filename
            output_file = output_dir / f"{base_name}.{start_row}-{end_row}{extension}"

            # Write the chunk with header
            with open(output_file, "w", newline="", encoding="utf-8") as out_f:
                writer = csv.writer(out_f)
                writer.writerow(header)
                writer.writerows(chunk)

            print(f"Created: {output_file}")
            chunk_num += 1

        if chunk_num == 0:
            print("No data rows found in the input file")
        else:
            print(f"Split complete: Created {chunk_num} files")


def main() -> None:
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Split a CSV file into multiple files with a maximum number of lines each."
    )
    parser.add_argument(
        "--input-csv", type=Path, required=True, help="Path to the input CSV file"
    )
    parser.add_argument(
        "--max-lines",
        type=int,
        required=True,
        help="Maximum number of data rows per output file (excluding header)",
    )

    args = parser.parse_args()

    # Validate input file
    if not args.input_csv.exists():
        print(f"Error: Input file '{args.input_csv}' does not exist")
        return

    if not args.input_csv.is_file():
        print(f"Error: '{args.input_csv}' is not a file")
        return

    # Validate max_lines
    if args.max_lines <= 0:
        print("Error: --max-lines must be a positive integer")
        return

    # Split the CSV
    split_csv(args.input_csv, args.max_lines)


if __name__ == "__main__":
    main()

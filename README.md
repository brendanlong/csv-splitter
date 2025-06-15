# CSV Splitter

A simple Python utility that splits large CSV files into smaller chunks while preserving headers.

## Features

- Split CSV files based on maximum number of rows per file
- Preserves header row in each output file
- Output files are named with row ranges (e.g., `input.1-5000.csv`)
- Type-safe with pyright strict mode
- UTF-8 encoding support

## Installation

Clone the repository and run the setup script:

```bash
git clone <repository-url>
cd csv-splitter
./setup.sh
```

This will:
- Install dependencies using uv
- Set up pre-commit hooks
- Configure the development environment

## Usage

```bash
python split_csv.py --input-csv <input_file.csv> --max-lines <number>
```

### Arguments

- `--input-csv`: Path to the input CSV file to split
- `--max-lines`: Maximum number of data rows per output file (excluding header)

### Example

Split a large CSV file into chunks of 5000 rows each:

```bash
python split_csv.py --input-csv data.csv --max-lines 5000
```

This will create files like:
- `data.1-5000.csv`
- `data.5001-10000.csv`
- `data.10001-15000.csv`
- etc.

Each output file will contain the original header row plus up to 5000 data rows.

## Development

This project uses:
- `pyright` for type checking (strict mode)
- `ruff` for linting and formatting
- `pre-commit` for git hooks
- `pytest` for testing

Run type checking:
```bash
pyright
```

Run linting:
```bash
ruff check .
```

Format code:
```bash
ruff format .
```

## Requirements

- Python >= 3.12
- No external dependencies for runtime (uses only standard library)

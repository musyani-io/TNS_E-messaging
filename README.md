# TNS E-messaging Project

## Overview

This project automates data extraction and personalized messaging (SMS/WhatsApp) for streamlined billing communication.

## Key Components

- **`scripts/data_extraction.py`**: Extracts and cleans data from source files (e.g., Excel), using `openpyxl` or `pandas`.
- **`scripts/extracted_csv.py`**: Handles CSV file extraction and processing.
- **`scripts/main.py`**: Orchestrates the core workflow: data processing, message handling, and execution via CLI arguments.
- **`scripts/miscallenous.py`**: Contains helper functions and utility code.
- **`scripts/templates.py`**: Populates message templates with client-specific data.

## Dependencies

- `openpyxl` (Excel data extraction)
- `requests` (HTTP requests for TextBee API)
- `python-dotenv` (Environment variable management)
- `csv` (CSV file handling)
- `tabulate` (Formatted table output)
- `flake8, flake8-comprehensions, flake8-docstrings` (Linting)

Install via: `pip install -r requirements.txt`

## Setup

1. Clone the repository.
2. Create a virtual environment: `python3 -m venv venv`
3. Activate: `source venv/bin/activate` (Linux/macOS) or `venv\Scripts\activate` (Windows)
4. Install dependencies: `pip install -r requirements.txt`
5. Configure environment variables in `.env`:

   ```
   API_KEY=<your_textbee_api_key>
   DEVICE_ID=<your_textbee_device_id>
   ```

## Usage

Run `scripts/main.py` with appropriate command-line arguments (see `--help` for options):

```bash
python scripts/main.py <command> --filename <filename> --name <name> --limit <limit>
```

Available commands: `display`, `extract`, `fill`, `send`

Coding style is enforced with `flake8`.

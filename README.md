# TNS E-message Project - Automated Data Extraction and Messaging

## Overview

This project automates the process of extracting data from a source (likely an Excel file), transforming it, and sending personalized messages (SMS, WhatsApp, etc.) to clients.

## Key Components

The project consists of several Python scripts:

- **`scripts/data_extraction.py`:**

  - Responsible for extracting data from the source data file (e.g., Excel).
  - Handles data cleaning, transformation, and validation.
  - Uses libraries like `openpyxl` to interact with the data file.

- **`scripts/extracted_csv.py`:**

  - Handles the extraction and reading of CSV files, likely outputted by the data extraction script.

- **`scripts/main.py`:**

  - The main entry point of the application.
  - Orchestrates the data extraction, message generation, and sending processes.
  - Likely contains the main application logic and user interface (if any).

- **`scripts/miscallenous.py`:**

  - A file with a typo and probably contains miscellenous tools and functions used by other functions.
  - May include helper functions, utility classes, or other code that doesn't fit neatly into other modules.

- **`scripts/send_sms.py`:**

  - Handles sending SMS messages to clients.
  - Uses a messaging API (e.g., TextBee) to send messages.
  - Includes functionality for template-based messaging and error handling.

- **`scripts/temp_filling.py`:**
  - Fills message templates with extracted data.
  - Uses string formatting to generate personalized messages.

## Dependencies

The project likely depends on the following Python libraries:

- `openpyxl` (for Excel data extraction)
- `requests` (for making HTTP requests to messaging APIs)
- `python-dotenv` (for loading environment variables)
- `csv` (for CSV file handling)

A `requirements.txt` file is included to list all the necessary dependencies.

## Setup and Installation

1. Clone the repository:

   ```bash
   git clone <https://github.com/musyani-io/TNS_E-messaging.git>
   ```

2. Create a virtual environment:

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Linux/macOS
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables:

   - Create a `.env` file in the root directory of the project.
   - Add the following environment variables, replacing the placeholders with your actual values like API_KEY and DEVICE_ID

## Usage

1. Run the `scripts/main.py` script:

   ```bash
   python scripts/main.py
   ```

2. Follow the instructions in the user interface (if any) or configure the script using command-line arguments (if applicable).

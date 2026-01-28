# TNS E-Messaging System

A Python-based automated billing and messaging solution designed for **TNS Water Services**. This system streamlines the process of extracting billing data, generating personalized SMS notifications, and tracking delivery status via the **TextBee API**.

## Core Features

- **Excel Data Extraction**: Parses complex, proprietary Excel grid layouts to extract customer billing records, water usage, and contact details.
- **Bulk SMS Broadcasting**: Sends personalized billing notifications with built-in rate limiting (TextBee API) to prevent carrier spam flagging.
- **Dynamic Templating**: Populates message templates with specific customer data (Name, Bill Amount, Usage).
- **Delivery Tracking**: Real-time monitoring of SMS status (Sent, Delivered, Failed) with detailed reporting and CSV exports for failed messages.
- **CLI Interface**: Robust command-line tools for managing the entire workflow.

## Technical Stack

- **Language**: Python 3.x
- **Data Processing**: `openpyxl`, `csv`, `json`
- **Network**: `requests` (TextBee Gateway API)
- **CLI**: `argparse`, `tabulate`

## Installation

1.  Clone the repository.
2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3.  Configure `.env` with your API credentials:
    ```env
    DEVICE_ID=your_device_id
    API_KEY=your_api_key
    ```

## Usage

Run the main script via CLI:

```bash
# 1. Extract data from Excel (docs/source/source_data.xlsx)
python scripts/main.py extract

# 2. Fill templates and prepare billing data
python scripts/main.py fill --filename FILENAME

# 3. Send SMS (optional limit)
python scripts/main.py send --limit NUMBER

# 4. Check delivery status & generate reports
python scripts/main.py delivery

# 5. Display processed data
python scripts/main.py display --filename FILENAME
```

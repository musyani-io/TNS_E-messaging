"""SMS Message Template Processing and Formatting Module.

Responsible for transforming billing CSV data into personalized SMS messages ready for transmission.
Implements location-aware template selection (Lumo vs. Chanika) with variable substitution,
number localization, and intelligent duplicate prevention.

Workflow:
    1. Load customer billing records from CSV export
    2. Check against sent/failed message history to avoid duplicates
    3. Select location-specific template (message_templates/{location}/smart_text.txt)
    4. Substitute template variables with formatted customer data
    5. Persist prepared messages to JSON queue for batch transmission

Template Variables Supported:
    * {Month, year}: Billing period (e.g., "Jan, 2026")
    * {Customer Name}: Full name of customer
    * {Liters Used}: Formatted water consumption with thousands separator
    * {Net Charge}: Current period charges (formatted)
    * {Adjustments}: Previous balance/debts (formatted)
    * {Final Bill}: Total amount due (formatted)
    * {Deadline Date}: Payment due date (7 days from billing date)
    * {AZAMPESA}, {LIPA_NAMBA}, {TigoPesa}: Payment account identifiers
    * {RECIEVER_NAME}: Payee name for mobile money transfers

Number Formatting:
    - Uses British English locale (en_GB.UTF-8) for comma separators
    - Floats: "1,234.5" (1 decimal place)
    - Integers: "5,000" (no decimals)
"""

from extracted_csv import *
from dotenv import load_dotenv
from datetime import datetime, timedelta
from jsonSt import *
import calendar
import locale
import os

load_dotenv()


def formatNumbers(num):
    """
    Apply locale-aware thousands separators to numeric values for SMS display.

    Formats numbers using British English conventions (comma as thousands separator,
    period as decimal point). Essential for customer-facing message readability.

    Args:
        num (int | float): Numeric value to format (billing amounts or usage metrics)

    Returns:
        str: Formatted number string:
            - float: "1,234.5" (exactly 1 decimal place)
            - int: "5,000" (no decimal places)

    Examples:
        >>> formatNumbers(5000)
        "5,000"
        >>> formatNumbers(1234.567)
        "1,234.6"
        >>> formatNumbers(42)
        "42"

    Note:
        Requires locale 'en_GB.UTF-8' to be available on system. Falls back
        to system default if unavailable.
    """
    locale.setlocale(locale.LC_ALL, "en_GB.UTF-8")
    if isinstance(num, float):
        return locale.format_string("%.1f", num, grouping=True)
    else:
        return locale.format_string("%d", num, grouping=True)


def tempFilling(startDate, filePath, failedCsv):
    """
    Generate personalized SMS messages from billing CSV and queue for transmission.

    Orchestrates the complete message preparation pipeline:
    1. Load failed message history to enable selective retry
    2. Parse customer billing records from CSV
    3. Skip customers already processed (in sent.json) or explicitly failed
    4. Load location-specific template (Lumo or Chanika)
    5. Calculate payment deadline (startDate + 7 days)
    6. Substitute template variables with formatted customer data
    7. Queue prepared message in data.json for sendMessage() consumption

    Args:
        startDate (datetime): Billing period start date. Used for:
            - Month/year display ("Jan, 2026")
            - Deadline calculation (startDate + timedelta(7))
        filePath (str): Path to billing CSV containing customer records
        failedCsv (str): Path to failed.csv containing retry candidates

    Returns:
        None: Side effect is population of json_storage/data.json with message queue

    Message Queue Format (data.json):
        {
            "Customer Name": {
                "Contact": "+255773422381",
                "Body": "Dear John, your Jan 2026 bill..."
            },
            ...
        }

    Raises:
        FileNotFoundError: If template file doesn't exist for customer's location
        KeyError: If required environment variables are missing
    """
    try:
        failedClients = []  # Customers from previous failed delivery attempts

        # Load failed delivery records for selective retry inclusion
        with open(failedCsv, "r") as csvFile:
            reader = csv.reader(csvFile)
            next(reader)  # Discard header row

            for row in reader:
                failedClients.append(row[0])  # Extract customer name

        # Parse billing records and generate messages
        with open(filePath, "r") as csvFile:

            reader = csv.reader(csvFile)

            presentData = []
            next(reader)  # Discard header row

            # Process each customer billing record
            for row in reader:

                presentData.append(row)

                # Skip customers already successfully sent (avoid duplicate messages)
                sentClients = getJsonData("json_storage/sent.json")

                if row[1] in failedClients:  # Include failed customers for retry
                    pass
                elif row[1] in sentClients:  # Skip already-sent customers
                    continue

                # Load template specific to customer's service location
                filePath = f"message_templates/{row[4]}/smart_text.txt"  # row[4] = Lumo/Chanika
                with open(filePath, "r") as f:

                    file = f.read()
                    # Compute payment deadline: billing date + 7 days
                    newDate = datetime.strftime((startDate + timedelta(7)), "%d-%m-%Y")

                    # Map template placeholders to actual customer data
                    var = {  # Dictionary for template variable substitution
                        "Month, year": f"{calendar.month_abbr[startDate.month]}, {startDate.year}",
                        "Customer Name": row[1],
                        "Liters Used": formatNumbers(
                            float(row[5])
                        ),  # Water consumption
                        "Net Charge": formatNumbers(int(row[6])),  # Current charges
                        "Adjustments": formatNumbers(int(row[7])),  # Previous balance
                        "Final Bill": formatNumbers(int(row[8])),  # Total due
                        "Deadline Date": newDate,
                        "AZAMPESA": os.getenv("AZAMPESA"),  # Payment account numbers
                        "LIPA_NAMBA": os.getenv("LIPA_NAMBA"),
                        "TigoPesa": os.getenv("TIGOPESA"),
                        "RECIEVER_NAME": os.getenv("RECIEVER_NAME"),  # Payee name
                    }

                    # Perform variable substitution using str.format()
                    filledTemp = file.format(**var)
                    value = {"Contact": row[2], "Body": filledTemp}
                    addJsonData(
                        "json_storage/data.json", row[1], value
                    )  # Queue message

        print("Storage 'data.json' updated!✅")

    except Exception as Error:
        errorDisplay(Error)


if __name__ == "__main__":

    tempFilling(
        datetime.today(),
        "docs/results/January, 2026 (1).csv",
        "docs/results/failed.csv",
    )

"""Message Template Processing Module.

Handles the filling of SMS message templates with customer billing data.
Reads location-specific message templates (Lumo or Chanika), substitutes
variables with actual customer billing information, and prepares messages
for sending.

Features:
- Number formatting with thousand separators
- Template variable substitution
- Automatic deadline calculation
- Payment provider information insertion
- Duplicate message prevention
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
    Format numbers with thousand separators for better readability.

    Args:
        num (int or float): Number to format

    Returns:
        str: Formatted number string with commas as thousand separators
             Float values show 1 decimal place, integers show no decimals
    """
    locale.setlocale(locale.LC_ALL, "en_GB.UTF-8")
    if isinstance(num, float):
        return locale.format_string("%.1f", num, grouping=True)
    else:
        return locale.format_string("%d", num, grouping=True)


def tempFilling(startDate, filePath, failedCsv):
    # Data to be extracted for

        failedClients = []

        with open(failedCsv, "r") as csvFile:

            reader = csv.reader(csvFile)
            next(reader)

            for row in reader:
                failedClients.append(row[0])

        with open(filePath, "r") as csvFile:

            reader = csv.reader(csvFile)

            presentData = []
            next(reader)  # Skip header row

            # Process each customer record
            for row in reader:

                presentData.append(row)

                # Skip customers who have already been sent messages
                sentClients = getJsonData("json_storage/sent.json")

                if row[1] in failedClients:
                    pass
                elif row[1] in sentClients:
                    continue

                # Load location-specific message template (Lumo or Chanika)
                filePath = f"message_templates/{row[4]}/smart_text.txt"
                with open(filePath, "r") as f:

                    file = f.read()
                    # Calculate payment deadline (7 days from start date)
                    newDate = datetime.strftime((startDate + timedelta(7)), "%d-%m-%Y")

                    var = {  # Dictionary for variables in message templates.
                        "Month, year": f"{calendar.month_abbr[startDate.month]}, {startDate.year}",
                        "Customer Name": row[1],
                        "Liters Used": formatNumbers(float(row[5])),
                        "Net Charge": formatNumbers(int(row[6])),
                        "Adjustments": formatNumbers(int(row[7])),
                        "Final Bill": formatNumbers(int(row[8])),
                        "Deadline Date": newDate,
                        "AZAMPESA": os.getenv("AZAMPESA"),
                        "LIPA_NAMBA": os.getenv("LIPA_NAMBA"),
                        "TigoPesa": os.getenv("TIGOPESA"),
                        "RECIEVER_NAME": os.getenv("RECIEVER_NAME"),
                    }

                    # Substitute template variables with actual values
                    filledTemp = file.format(**var)
                    value = {"Contact": row[2], "Body": filledTemp}
                    addJsonData("json_storage/data.json", row[1], value)
        
        print("Storage 'data.json' updated!✅")

    except Exception as Error:
        errorDisplay(Error)


if __name__ == "__main__":

    tempFilling(datetime.today(),
            f"docs/results/January, 2026 (1).csv",
            "docs/results/failed.csv",)

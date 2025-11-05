from extracted_csv import *
from dotenv import load_dotenv
from datetime import datetime, timedelta
from jsonSt import *
import os

load_dotenv()


def tempFilling(startDate, filePath, fileName):
    # Data to be extracted for

    try:

        with open(filePath, "r") as csvFile:

            reader = csv.reader(csvFile)

            presentData = []
            next(reader)

            for row in reader:

                presentData.append(row)

                filePath = f"message_templates/{row[4]}/smart_text.txt"
                with open(filePath, "r") as f:

                    file = f.read()
                    newDate = datetime.strftime((startDate + timedelta(7)), "%d-%m-%Y")

                    var = {  # Dictionary for variables in message templates.
                        "Month, year": fileName,
                        "Customer Name": row[1],
                        "Liters Used": row[5],
                        "Net Charge": row[6],
                        "Adjustments": row[7],
                        "Final Bill": row[8],
                        "Deadline Date": newDate,
                        "AZAMPESA": os.getenv("AZAMPESA"),
                        "LIPA_NAMBA": os.getenv("LIPA_NAMBA"),
                        "TigoPesa": os.getenv("TIGOPESA"),
                    }

                    filledTemp = file.format(**var)
                    store = "json_storage/data.json"
                    jsonCreate(store)
                    value = {"Contact": row[2], "Body": filledTemp}
                    addJsonData(store, row[1], value)

    except Exception as Error:
        errorDisplay(Error)


if __name__ == "__main__":

    print(tempFilling("docs/results/Oct, 2025.csv", "Oct-2024"))

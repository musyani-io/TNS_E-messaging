import csv
import sys
from datetime import datetime, timedelta


def fillTemp(tempPath, var):
    # Read the file first
    try:
        with open(tempPath, "r") as temp:
            file = temp.read()
            filled = file.format(**var)

            print(filled)

    except Exception as Error:
        print(f"Error: {type(Error).__name__} - {Error}")


def readCsv(fileName):

    try:
        filePath = f"docs/results/{fileName}.csv"

        with open(filePath, "r") as csvFile:
            reader = csv.reader(csvFile)

            next(reader)
            rows = []
            for row in reader:

                startDate = datetime.strptime(row[0], "%d-%b-%Y")
                newDate = datetime.strftime((startDate + timedelta(7)), "%d-%m-%Y")

                var = {  # Dictionary for variables in message templates.
                    "Month, year": fileName,
                    "Customer Name": row[1],
                    "Liters Used": row[5],
                    "Net Charge": row[6],
                    "Adjustments": row[7],
                    "Final Bill": row[8],
                    "Deadline Date": newDate,
                }

                tempPath = "message_templates/Chanika/smart_text.txt"
                fillTemp(tempPath, var)

    except Exception as Error:
        print(f"Error: {type(Error).__name__} - {Error}")
        sys.exit(1)


if __name__ == "__main__":
    readCsv("Aug, 2024")

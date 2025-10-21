import os
import csv
import sys


def fileCreation(fileName):

    filePath = f"docs/results/{fileName}.csv"
    if not os.path.exists(filePath):

        try:

            with open(filePath, "w", newline="") as csvFile:

                writer = csv.writer(csvFile)
                headers = [
                    "Reading Date",
                    "Customer Name",
                    "Contacts",
                    "Communication App",
                    "Liters Used",
                    "Net Charge",
                    "Adjustments",
                    "Final Bill",
                ]

                writer.writerow(headers)
                print(f"File {fileName} created!✅")

        except Exception as Error:
            print(f"Error: {type(Error).__name__} - {Error}")
            sys.exit(1)


def addCsvData(fileName, info):

    filePath = f"docs/results/{fileName}.csv"

    try:
        with open(filePath, "a", newline="") as csvFile:

            writer = csv.writer(csvFile)
            writer.writerows(info)

    except Exception as Error:
        print(f"Error: {type(Error).__name} - Error")
        sys.exit(1)

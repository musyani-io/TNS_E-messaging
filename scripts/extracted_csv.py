from datetime import datetime
from pprint import pprint
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
                    "Location",
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

    rowList = []

    try:
        with open(filePath, "r") as csvFile:

            date = datetime.strptime("22-Aug-2024", "%d-%b-%Y")

            for row in info:

                date2 = datetime.strptime(row[0], "%d-%b-%Y")
                if (date == date2) and (row[1] is not None) and (row[5] > 1):
                    rowList.append(row)
            
        with open(filePath, "a", newline="") as csvFile:

            writer = csv.writer(csvFile)
            writer.writerows(rowList)


    except Exception as Error:
        print(f"Error: {type(Error).__name__} - {Error}")
        sys.exit(1)

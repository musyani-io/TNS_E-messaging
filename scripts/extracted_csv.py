from datetime import datetime, timedelta
from miscallenous import errorDisplay
import os
import csv


def fileCreation(fileName, headers):

    filePath = f"docs/results/{fileName}.csv"
    if not os.path.exists(filePath):

        try:

            with open(filePath, "w", newline="") as csvFile:

                writer = csv.writer(csvFile)
                writer.writerow(headers)

                print(f"File {fileName} created!✅")

        except Exception as Error:
            errorDisplay(Error)


def addRows(fileName, info, date):

    filePath = f"docs/results/{fileName}.csv"

    try:

        with open(filePath, "a", newline="") as csvFile:

            writer = csv.writer(csvFile)

            data = nonRecInput(filePath, info)
            writer.writerows(data)

        print(f"{fileName} updated✅")

    except Exception as Error:
        errorDisplay(Error)


def nonRecInput(filePath, data):    # Prevents existing rows to being added to the CSV

    try:

        with open(filePath, "r", newline="") as csvFile:

            reader = csv.reader(csvFile)

            presList = []
            for rows in reader:
                presList.append(rows)

            updList = []
            for line in data:
                if line not in presList:
                    updList.append(line)

            return updList

    except Exception as Error:
        errorDisplay(Error)

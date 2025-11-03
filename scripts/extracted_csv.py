from datetime import datetime, timedelta
import os
import csv
import sys


def fileCreation(fileName, headers):

    filePath = f"docs/results/{fileName}.csv"
    if not os.path.exists(filePath):

        try:

            with open(filePath, "w", newline="") as csvFile:

                writer = csv.writer(csvFile)
                writer.writerow(headers)

                print(f"File {fileName} created!✅")

        except Exception as Error:
            print(f"Error: {type(Error).__name__} - {Error}")
            sys.exit(1)


def addRows(fileName, info, date):

    filePath = f"docs/results/{fileName}.csv"

    try:

        with open(filePath, "a", newline="") as csvFile:

            writer = csv.writer(csvFile)

            data = activeClients(filePath, info, date)
            writer.writerows(data)

        print(f"{fileName} updated✅")

    except Exception as Error:
        print(f"Error: {type(Error).__name__} - {Error}")
        sys.exit(1)


def activeClients(filePath, data, date):    # Prevents existing rows to being added to the CSV

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
        print(f"Error: {type(Error).__name__} - {Error}")
        sys.exit(1)

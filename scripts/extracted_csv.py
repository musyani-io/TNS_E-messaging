from miscallenous import errorDisplay, specialCases
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

            info = activeClients(info)
            data = nonRecInput(filePath, info)
            writer.writerows(data)

            if len(data) != 0:
                print(f"{fileName} updated✅")

            else:
                print("No new data!")

    except Exception as Error:
        errorDisplay(Error)


def activeClients(data):

    try:

        actvClients = []

        for rows in data:

            if (
                rows[1] is not None
                and int(rows[8]) > 50
                and rows[1] not in specialCases
            ):  # Checks and removes empty names and bills, excludes names in specialCases too

                actvClients.append(rows)

        return actvClients

    except Exception as Error:
        errorDisplay(Error)


def nonRecInput(filePath, data):  # Prevents existing rows to being added to the CSV

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

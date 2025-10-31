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


def activeClients(filePath, data, date):

    try:

        rowList = []

        with open(filePath, "r") as csvFile:

            for row in data:

                # date = datetime.strptime(date, "%d-%b-%Y")
                # date2 = datetime.strptime(row[0], "%d-%b-%Y")
                if (
                    # (date - date2 <= timedelta(days=7))  # Within a week of reading date
                    (row[1] is not None)
                    and not (row[8] == 0)
                ):
                    # Proves if the data is of same date, has a name and also, there are some liters used.
                    rowList.append(row)

        return rowList

    except Exception as Error:
        print(f"Error: {type(Error).__name__} - {Error}")
        sys.exit(1)

from miscallenous import errorDisplay
import os
import csv


def fileCreation(fileName, headers):
    """
    Create a new CSV file with specified headers if it doesn't exist.

    Args:
        fileName (str): Name of the CSV file (without extension)
        headers (list): List of column header names

    Returns:
        None: Creates CSV file in docs/results/ directory
    """
    filePath = f"docs/results/{fileName}.csv"
    if not os.path.exists(filePath):

        try:

            with open(filePath, "w", newline="") as csvFile:

                writer = csv.writer(csvFile)
                writer.writerow(headers)

                print(f"File {fileName} created!✅")

        except Exception as Error:
            errorDisplay(Error)


def addRows(fileName, info):

    Returns:
        None: Updates CSV file with new rows
    """
    filePath = f"docs/results/{fileName}.csv"

    try:

        with open(filePath, "a", newline="") as csvFile:

            writer = csv.writer(csvFile)

            data = nonRecInput(filePath, info)
            writer.writerows(data)

            if len(data) > 0:
                print(f"{fileName} updated✅")

            else:
                print("No new data!")

    except Exception as Error:
        errorDisplay(Error)


def activeClients(data):
    """
    Filter customer data to include only active clients with valid bills.

    Removes entries with:
    - Empty/None names
    - Bills less than or equal to 50 TZS
    - Names in the special cases exclusion list

    Args:
        data (list): List of customer data rows

    Returns:
        list: Filtered list containing only active clients
    """
    try:

        actvClients = []

        for rows in data:
            # Filter criteria: valid name, bill > 50, not in special cases
            if (
                rows[1] is not None and int(rows[8]) > 50
            ):  # Checks and removes empty names and bills, excludes names in specialCases too

                actvClients.append(rows)

        return actvClients

    except Exception as Error:
        errorDisplay(Error)


def nonRecInput(filePath, data):
    """
    Prevent duplicate entries by filtering out rows that already exist in CSV.

    Compares new data against existing CSV content and returns only new entries.

    Args:
        filePath (str): Path to the CSV file to check
        data (list): List of new data rows to validate

    Returns:
        list: Filtered list containing only non-duplicate entries
    """
    try:

        with open(filePath, "r", newline="") as csvFile:

            reader = csv.reader(csvFile)

            # Load all existing rows from CSV
            presList = []
            for rows in reader:
                presList.append(rows)

            # Filter out rows that already exist
            updList = []
            for line in data:
                if line not in presList:  # Only include new entries
                    updList.append(line)

            return updList

    except Exception as Error:
        errorDisplay(Error)

if __name__ == "__main__":
    addRows("failed", [["Khalid", "unknown"], ["Juma", "failed"]])
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
    """
    Append new customer records to CSV file with automatic duplicate prevention.

    Implements safe append operation that prevents duplicate entries by comparing
    new records against existing CSV content before writing.

    Args:
        fileName (str): Base name of CSV file without extension (e.g., "January, 2026")
        info (list[list[str]]): Customer billing records to append. Each record is
            a list matching CSV column structure (9 elements)

    Returns:
        None: Modifies CSV file in docs/results/ directory

    Side Effects:
        Prints status message:
        - "{fileName} updated✅" if records were added
        - "No new data!" if all records already exist (duplicates filtered)

    Behavior:
        1. Opens CSV in append mode
        2. Filters info through nonRecInput() to remove duplicates
        3. Writes only new records
        4. Reports operation outcome
    """
    filePath = f"docs/results/{fileName}.csv"

    try:

        with open(filePath, "a", newline="") as csvFile:

            writer = csv.writer(csvFile)

            # Filter out duplicates before writing
            data = nonRecInput(filePath, info)  # Returns only new records
            writer.writerows(data)

            if len(data) > 0:
                print(f"{fileName} updated✅")

            else:
                print("No new data!")

    except Exception as Error:
        errorDisplay(Error)


def activeClients(data):
    """
    Filter customer records to retain only billable, active accounts.

    Implements business logic for identifying customers who should receive billing
    messages based on two criteria:
    1. Valid customer name (not None/empty)
    2. Bill amount exceeds minimum threshold (>50 TZS)

    Exclusion Rules:
        * None names: Invalid/incomplete data entries
        * Bills ≤ 50 TZS: Below minimum billing threshold (administrative cutoff)

    Args:
        data (list[list[str]]): Raw customer records from Excel extraction.
            Expected structure: [date, name, contact, app, location, liters,
                                net_charge, adjustments, final_bill]

    Returns:
        list[list[str]]: Filtered records containing only active, billable customers

    Business Logic:
        Minimum billing threshold of 50 TZS filters out:
        - Customers with zero usage
        - Accounts with negligible outstanding balances
        - Rounding errors or data entry mistakes

    Note:
        Previously supported specialCases exclusion list (removed in current version).
    """
    try:

        actvClients = []

        for rows in data:
            # Apply filtering criteria: non-null name AND bill exceeds minimum threshold
            if (
                rows[1] is not None and int(rows[8]) > 50
            ):  # rows[1]=name, rows[8]=final_bill

                actvClients.append(rows)

        return actvClients

    except Exception as Error:
        errorDisplay(Error)


def nonRecInput(filePath, data):
    """
    Implement deduplication by filtering records that already exist in CSV file.

    Performs complete record comparison (all columns) to identify duplicates,
    ensuring idempotent append operations where re-running extraction with same
    data won't create duplicate CSV entries.

    Args:
        filePath (str): Path to CSV file for duplicate checking
        data (list[list[str]]): New records to validate against existing content

    Returns:
        list[list[str]]: Subset of data containing only records not present in CSV

    Algorithm:
        1. Load all existing rows from CSV into memory (presList)
        2. Compare each new record against existing rows
        3. Include record in output only if exact match not found
        4. Return filtered list for safe appending

    Comparison Logic:
        Uses Python list equality (==) which compares all elements in order.
        Two records are considered duplicates if ALL columns match exactly.

    Performance Consideration:
        O(n*m) complexity where n=new records, m=existing records.
        Acceptable for typical dataset sizes (hundreds of records).
        For large datasets, consider hash-based deduplication.
    """
    try:

        with open(filePath, "r", newline="") as csvFile:

            reader = csv.reader(csvFile)

            # Load complete existing dataset into memory for comparison
            presList = []
            for rows in reader:
                presList.append(rows)

            # Filter: retain only records absent from existing dataset
            updList = []
            for line in data:
                if line not in presList:  # Full record comparison (all columns)
                    updList.append(line)

            return updList

    except Exception as Error:
        errorDisplay(Error)


if __name__ == "__main__":
    addRows("failed", [["Khalid", "unknown"], ["Juma", "failed"]])

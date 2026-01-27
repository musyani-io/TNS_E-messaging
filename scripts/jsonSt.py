"""JSON Storage Management Module.

Provides utilities for managing JSON-based data storage for the messaging system.
Handles creation, reading, updating, and deletion of message data stored in JSON format.

Main storage files:
- data.json: Prepared messages awaiting sending
- sent.json: Messages that have been sent with their status
- delivery.json: Delivery status tracking

Features:
- Safe JSON file creation
- CRUD operations for JSON data
- Automatic cleanup of successfully sent messages
- CSV export for delivery tracking
"""

from miscallenous import errorDisplay
from extracted_csv import fileCreation
import csv
import json
import os


def jsonCreate(storagePath):
    """
    Create a new JSON storage file if it doesn't exist.

    Args:
        storagePath (str): Path where the JSON file should be created

    Returns:
        None: Creates an empty JSON file with an empty dictionary
    """
    try:
        # Check if file exists, create if not
        if not os.path.exists(storagePath):
            # Create a json file
            with open(storagePath, "x") as store:

                task = {}
                json.dump(task, store, indent=4)
                print("Storage file created✅")

    except Exception as Error:
        errorDisplay(Error)


def getJsonData(storagePath):
    """
    Read and return data from a JSON storage file.

    Args:
        storagePath (str): Path to the JSON file to read

    Returns:
        dict: Dictionary containing the JSON data
    """
    try:
        # Load and return JSON data from file
        with open(storagePath, "r") as store:

            presentData = json.load(store)

            return presentData

    except Exception as Error:
        errorDisplay(Error)


def addJsonData(storagePath, key, value):
    """
    Add or update a key-value pair in a JSON storage file.

    Args:
        storagePath (str): Path to the JSON file
        key (str): Key to add or update
        value (any): Value to associate with the key (typically dict)

    Returns:
        None: Updates the JSON file with new data
    """
    try:
        # Load existing data, add new entry, and save back
        presentData = getJsonData(storagePath)
        with open(storagePath, "w") as store:

            presentData[key] = value
            json.dump(presentData, store, indent=4)

    except Exception as Error:
        errorDisplay(Error)


def delJsonData(checkPath, deletePath):
    """
    Delete successfully sent message entries from the main data storage.

    Compares sent messages (with status 201) in checkPath against data in deletePath,
    and removes successfully sent entries from deletePath.

    Args:
        checkPath (str): Path to JSON file containing sent message statuses
        deletePath (str): Path to JSON file to delete entries from

    Returns:
        None: Updates deletePath file with entries removed
    """
    try:
        # Load data from both files
        sentData = getJsonData(checkPath)
        presentData = getJsonData(deletePath)
        presentNames = list(presentData.keys())
        sentNames = list(sentData.keys())

        # Iterate through sent messages and remove successful ones
        for i in range(len(sentNames)):

            sentName = sentNames[i]

            # Check if message was successfully sent (status 201) and exists in present data
            if (
                sentData[sentName]["Status"] == 201 and sentName in presentNames
            ):  # Checks for a successful request

                del presentData[sentName]  # Delete the successful entry from data.json

        with open(deletePath, "w") as file:

            json.dump(presentData, file, indent=4)

    except Exception as Error:
        errorDisplay(Error)


def jsonToCsv(jsonPath, csvPath):
    """
    Convert successfully delivered messages from JSON to CSV format.

    Extracts messages with status 201 (delivered) from JSON file and appends
    new entries to a CSV file, avoiding duplicates.

    Args:
        jsonPath (str): Path to JSON file containing message statuses
        csvPath (str): Name/path for the output CSV file

    Returns:
        None: Updates CSV file with newly delivered messages
    """
    try:
        # Initialize lists for tracking delivered messages
        deliveredList = []
        validRow = []
        fileCreation(csvPath, headers=["Name", "Status"])
        with open(jsonPath, "r") as file:

            data = json.load(file)

            names = list(data.keys())

            # Extract all successfully delivered messages (status 201)
            for name in names:
                if data[name]["Status"] == 201:
                    deliveredList.append([name, "Delivered"])

        # Check for duplicates against existing CSV file
        with open("docs/results/delivered.csv", "r", newline="") as csvFile:

            reader = csv.reader(csvFile)

            # Filter out entries that already exist in CSV
            for name in deliveredList:
                if name not in reader:
                    validRow.append(name)

        # Append only new entries to CSV file
        with open("docs/results/delivered.csv", "a", newline="") as csvFile:

            writer = csv.writer(csvFile)

            writer.writerows(validRow)

            # Display status message
            if len(validRow) > 0:
                print("Delivery file updated!✅")
            else:
                print("No new delivered contact")

    except Exception as Error:
        errorDisplay(Error)


if __name__ == "__main__":

    jsonToCsv("json_storage/sent.json", "delivered")

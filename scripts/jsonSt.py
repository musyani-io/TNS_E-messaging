"""JSON-Based Persistent Storage Management for Messaging System.

Provides CRUD operations for JSON files used as lightweight database for the messaging workflow.
Manages three primary storage files with distinct lifecycle stages:

1. data.json (Message Queue)
   - Prepared messages awaiting transmission
   - Structure: {"Customer Name": {"Contact": "+255...", "Body": "..."}, ...}
   - Populated by: tempFilling()
   - Consumed by: sendMessage()

2. sent.json (Transmission Log)
   - Successfully transmitted messages with batch tracking
   - Structure: {"Customer Name": {"smsBatchId": "...", "Contact": "...", "Status": 201}, ...}
   - Populated by: sendMessage()
   - Consumed by: deliveryMessage()

3. delivery.json (Status Archive)
   - Final delivery status from TextBee API
   - Structure: {"Customer Name": {"type": "sms", "status": "delivered"}, ...}
   - Populated by: deliveryMessage()

Operations:
    * jsonCreate(): Safe file initialization (skip if exists)
    * getJsonData(): Load and parse JSON file to dict
    * addJsonData(): Insert/update key-value pair
    * delJsonData(): Remove successfully sent messages from queue
    * jsonToCsv(): Export delivered messages to CSV format

Thread Safety: Not thread-safe. Sequential execution assumed.
"""

from miscallenous import errorDisplay
from extracted_csv import fileCreation
import csv
import json
import os


def jsonCreate(storagePath):
    """
    Initialize JSON storage file with empty dictionary if not already present.

    Implements safe file creation using exclusive mode ('x') to prevent accidental
    overwrites. Silently skips creation if file already exists.

    Args:
        storagePath (str): Target filesystem path for JSON file

    Returns:
        None: Creates file with content '{}' and prints confirmation,
              or no-op if file exists

    Raises:
        PermissionError: If process lacks write permissions for target directory
        OSError: If path contains invalid characters or exceeds system limits

    Note:
        Uses indent=4 for human-readable formatting of JSON output.
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
    Load and parse JSON file contents into Python dictionary.

    Args:
        storagePath (str): Path to JSON file to read

    Returns:
        dict: Parsed JSON data structure. Returns empty dict {} if file is empty.

    Raises:
        FileNotFoundError: If specified path doesn't exist
        json.JSONDecodeError: If file contains malformed JSON syntax
        PermissionError: If process lacks read permissions

    Usage:
        >>> data = getJsonData("json_storage/sent.json")
        >>> print(data.keys())  # Access customer names
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
    Insert or update key-value pair in JSON storage file.

    Implements atomic update pattern:
    1. Load existing JSON data
    2. Modify in-memory dictionary
    3. Write complete dictionary back to file

    Args:
        storagePath (str): Path to JSON file to modify
        key (str): Dictionary key (typically customer name)
        value (Any): Value to associate with key (typically dict with Contact/Body or status info)

    Returns:
        None: Modifies file in-place with pretty-printed JSON (indent=4)

    Warning:
        Not atomic at filesystem level. Concurrent writes may cause data loss.
        Ensure sequential execution in production.

    Example:
        >>> addJsonData("data.json", "John Doe", {"Contact": "+255...", "Body": "..."})
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
    Purge successfully transmitted messages from message queue.

    Cross-references sent message log (checkPath) against message queue (deletePath),
    removing entries with HTTP 201 (Created) status to prevent duplicate sending.

    Workflow:
    1. Load sent messages from checkPath (sent.json)
    2. Load pending messages from deletePath (data.json)
    3. Identify messages with Status=201 AND present in pending queue
    4. Delete matched entries from pending queue
    5. Write cleaned queue back to deletePath

    Args:
        checkPath (str): Path to sent message log (e.g., "json_storage/sent.json")
        deletePath (str): Path to message queue (e.g., "json_storage/data.json")

    Returns:
        None: Modifies deletePath file in-place, removing successfully sent entries

    Status Code Reference:
        * 201: Message successfully accepted by TextBee API (safe to delete)
        * Other: Retain in queue for potential retry
    """
    try:
        # Load both storage files for cross-reference
        sentData = getJsonData(checkPath)  # Transmission log
        presentData = getJsonData(deletePath)  # Message queue
        presentNames = list(presentData.keys())
        sentNames = list(sentData.keys())

        # Identify and remove successfully transmitted messages
        for i in range(len(sentNames)):

            sentName = sentNames[i]

            # Deletion criteria: HTTP 201 status AND still present in queue
            if (
                sentData[sentName]["Status"] == 201 and sentName in presentNames
            ):  # 201 = "Created" (successful API acceptance)

                del presentData[sentName]  # Remove from queue to prevent resending

        with open(deletePath, "w") as file:

            json.dump(presentData, file, indent=4)

    except Exception as Error:
        errorDisplay(Error)


def jsonToCsv(jsonPath, csvPath):
    """
    Export successfully delivered messages from JSON to CSV format for archival.

    Extracts all messages with HTTP 201 status from JSON log and appends them to
    a CSV file, implementing duplicate detection to prevent redundant entries.

    Process:
    1. Create CSV file if it doesn't exist (headers: Name, Status)
    2. Load message status data from JSON
    3. Filter for Status==201 (successful delivery)
    4. Check against existing CSV entries
    5. Append only new (non-duplicate) deliveries
    6. Report number of records added

    Args:
        jsonPath (str): Path to JSON file containing message statuses (e.g., "sent.json")
        csvPath (str): Name for CSV file (created in docs/results/ directory)

    Returns:
        None: Creates/updates {csvPath}.csv with delivery records

    Side Effects:
        Prints status message:
        - "Delivery file updated!✅" if new records added
        - "No new delivered contact" if all records already exist

    CSV Format:
        Name,Status
        John Doe,Delivered
        Jane Smith,Delivered
    """
    try:
        # Initialize tracking lists for delivery records
        deliveredList = []  # All successfully delivered messages from JSON
        validRow = []  # New deliveries not yet in CSV (after deduplication)

        fileCreation(csvPath, headers=["Name", "Status"])
        with open(jsonPath, "r") as file:

            data = json.load(file)
            names = list(data.keys())

            # Extract all messages with successful status code
            for name in names:
                if data[name]["Status"] == 201:  # HTTP 201 = successful creation
                    deliveredList.append([name, "Delivered"])

        # Deduplication: compare against existing CSV records
        with open("docs/results/delivered.csv", "r", newline="") as csvFile:

            reader = csv.reader(csvFile)

            # Filter out records that already exist in CSV
            for name in deliveredList:
                if name not in reader:  # Only include truly new deliveries
                    validRow.append(name)

        # Append deduplicated records to CSV archive
        with open("docs/results/delivered.csv", "a", newline="") as csvFile:

            writer = csv.writer(csvFile)
            writer.writerows(validRow)

            # Provide user feedback on operation result
            if len(validRow) > 0:
                print("Delivery file updated!✅")
            else:
                print("No new delivered contact")

    except Exception as Error:
        errorDisplay(Error)


if __name__ == "__main__":

    jsonToCsv("json_storage/sent.json", "delivered")

"""TNS E-Messaging System - Main Application Module.

Provides the primary interface for Tanzania Water Service billing and messaging operations.
This module orchestrates the complete workflow from data extraction to SMS delivery,
integrating with TextBee API for reliable message transmission.

Core Capabilities:
    * Display customer billing records (full table or statistical summary)
    * Extract structured data from formatted Excel worksheets
    * Generate personalized SMS messages using template substitution
    * Transmit bulk SMS messages with configurable limits and rate control
    * Monitor and report delivery status with comprehensive metrics

CLI Usage Examples:
    $ python main.py display --filename "January, 2026 (1)"
    $ python main.py extract
    $ python main.py fill --filename "January, 2026 (1)"
    $ python main.py send --limit 10
    $ python main.py delivery

Author: TNS Water Services
API Provider: TextBee (https://textbee.dev)
"""

from data_extraction import *
from tabulate import tabulate
from templates import tempFilling, formatNumbers
from jsonSt import *
import argparse
import csv
import os
import requests
import time
import sys


def displayData(fileName, headers):
    """
    Render customer billing data from CSV file with user-selectable display modes.

    Provides two visualization modes:
    1. Full Mode: Complete tabular display of all customer records
    2. Summary Mode: Aggregated statistics including client counts by location,
       financial totals, and segmented billing breakdowns

    Args:
        fileName (str): CSV filename located in docs/results/ (e.g., "January, 2026.csv")
        headers (list[str]): Column names for table header row

    Returns:
        None: Outputs formatted table directly to console via tabulate

    Raises:
        FileNotFoundError: If specified CSV file doesn't exist
        ValueError: If CSV data contains invalid numeric values
    """
    try:
        # Configure file path and initialize accumulator variables
        dataPath = f"docs/results/{fileName}"
        row = []
        lumoCli = 0  # Lumo location client count
        chnkCli = 0  # Chanika location client count
        currCharges = 0  # Sum of current period charges
        adjs = 0  # Sum of previous period adjustments/debts
        sum = 0  # Grand total of all charges

        with open(dataPath, "r") as csvFile:

            reader = csv.reader(csvFile)
            next(reader)  # Discard header row

            # Parse each customer record and compute running totals
            for rows in reader:
                row.append(rows)

                # Segment clients by service location
                if rows[4] == "Lumo":
                    lumoCli += 1
                else:
                    chnkCli += 1

                # Accumulate financial metrics (columns: netCharge, adjustments, finalBill)
                currCharges += int(rows[6])
                adjs += int(rows[7])
                sum += int(rows[8])

            parameter = input("What should be displayed? (full or summary): ")
            print("")

            if parameter == "full":

                table = tabulate(row, headers, tablefmt="grid")
                print(table)

            elif parameter == "summary":

                clientNum = len(row)
                headers = ["Details", "Amount"]
                row = [
                    ["Lumo clients", lumoCli],
                    ["Chanika clients", chnkCli],
                    ["Total clients", clientNum],
                    ["Current Bills", formatNumbers(currCharges)],
                    ["Previous debts", formatNumbers(adjs)],
                    ["Total Bills", formatNumbers(sum)],
                ]

                table = tabulate(row, headers, tablefmt="grid")
                print(table)

            else:

                print("Error: Invalid command!")
                sys.exit(1)

    except Exception as Error:
        errorDisplay(Error)


def extractData(sourcePath):
    """
    Parse customer billing information from Excel workbook and export to CSV format.

    Orchestrates the complete extraction pipeline:
    1. Load Excel workbook and identify target worksheet
    2. Navigate cell grid to locate customer data boxes
    3. Extract and validate billing records
    4. Filter for active clients (bills > 50 TZS)
    5. Write results to timestamped CSV file
    6. Initialize JSON storage for messaging workflow

    Args:
        sourcePath (str): Absolute or relative path to source Excel file (.xlsx)

    Returns:
        None: Side effects include CSV file creation and JSON storage initialization

    Raises:
        SystemExit: If source file path is invalid or inaccessible
    """
    if os.path.exists(sourcePath):
        # Initialize extraction context: load workbook and get target worksheet reference
        workSheet, fileName = envSetup(sourcePath)
        cell = workSheet["A1"]  # Start iteration from top-left cell

        customerInfo = iterateOnBoxes(cell)
        fileCreation(
            fileName,
            headers=[
                "Reading Date",
                "Customer Name",
                "Contacts",
                "Communication App",
                "Location",
                "Liters Used",
                "Net Charge",
                "Adjustments",
                "Final Bill",
            ],
        )
        # Filter for billable clients: exclude empty records and bills ≤ 50 TZS
        customerInfo = activeClients(customerInfo)
        addRows(fileName, customerInfo)

        # Initialize persistent JSON storage for message queue and delivery tracking
        jsonCreate("json_storage/data.json")
        jsonCreate("json_storage/sent.json")

    else:

        print("Error: Source File Path not Found!")
        sys.exit(1)


def sendMessage(limit):
    """
    Transmit SMS billing notifications to customers via TextBee Gateway API.

    Implements batch message transmission with the following controls:
    - Automatic rate limiting (1 second delay between requests)
    - Configurable message limit (default: 40, range: 1-40)
    - Success tracking via JSON persistence
    - Automatic cleanup of successfully sent messages from queue

    Args:
        limit (int | None): Maximum messages to send in this batch.
            - None or invalid values default to 40
            - Values < 1 or > 40 are clamped to valid range
            - Cannot exceed total available recipients

    Returns:
        None: Updates sent.json with batch IDs and status codes,
              removes successful entries from data.json queue

    Raises:
        HTTPError: If TextBee API returns non-2xx status code
        KeyError: If environment variables (DEVICE_ID, API_KEY) are undefined
    """
    load_dotenv()
    store = "json_storage/sent.json"
    storagePath = "json_storage/data.json"

    try:
        # Construct TextBee REST API endpoint with device identifier
        baseUrl = "https://api.textbee.dev/api/v1"
        requestUrl = f"{baseUrl}/gateway/devices/{os.getenv("DEVICE_ID")}/send-sms"

        # Configure authentication and content type headers
        headers = {
            "x-api-key": os.getenv("API_KEY"),  # API key for gateway authorization
            "Content-Type": "application/json",  # JSON payload encoding
        }

        data = getJsonData(storagePath)
        names = list(data.keys())

        # Normalize and constrain message limit to acceptable range
        if limit is not None:
            # Enforce boundaries: min=1, max=40 or total_recipients (whichever is smaller)
            if limit > 40 or limit < 1:
                if limit > len(names):
                    limit = len(names)
                else:
                    limit = 40
        else:
            limit = 40

        # Iterate through message queue and transmit each SMS
        for i in range(limit):

            name = names[i]
            value = data[name]
            # Debug output (disabled): print(f"Name: {name}, Contact: {value["Contact"]}, Body: {value["Body"]}")

            # Construct TextBee-compliant SMS payload
            payload = {
                "message": value["Body"],
                # "recipients": ["+255773422381"],  # Reserved for testing - production disabled
                "recipients": [value["Contact"]],  # TextBee API requires array format
            }

            # Execute HTTP POST request to TextBee gateway
            response = requests.post(
                url=requestUrl, headers=headers, data=json.dumps(payload)
            )
            response.raise_for_status()  # Raise exception for HTTP errors (4xx/5xx)
            time.sleep(1)  # Rate control: 1-second inter-request delay

            # Persist transmission metadata for delivery tracking
            status = {
                "smsBatchId": response.json()["data"]["smsBatchId"],
                "Contact": value["Contact"],
                "Status": response.status_code,
            }
            addJsonData(store, name, status)
            delJsonData(store, storagePath)

            # return response.json()
            print(f"Request for {name} is sent✅")

    except Exception as Error:
        errorDisplay(Error)


def deliveryMessage():
    """
    Query message delivery status from TextBee API and generate comprehensive report.

    Performs batch status verification for all previously sent messages:
    1. Retrieves SMS batch IDs from sent.json storage
    2. Queries TextBee API for current delivery status of each batch
    3. Categorizes messages by status: sent, delivered, failed, pending, unknown
    4. Generates statistical summary with counts and success percentages
    5. Exports failed messages to dedicated CSV for retry handling

    Status Definitions:
        * sent: Accepted by carrier but not yet delivered
        * delivered: Successfully received by recipient device
        * failed: Permanent delivery failure (invalid number, carrier rejection)
        * pending: Awaiting carrier acceptance
        * unknown: Status unavailable from carrier

    Returns:
        None: Outputs tabulated statistics to console and updates delivery.json

    Side Effects:
        - Creates/updates delivery.json with status metadata
        - Creates/updates failed.csv with undelivered message records
    """
    try:
        # Configure storage paths and load transmission history
        sentPath = "json_storage/sent.json"
        deliveryPath = "json_storage/delivery.json"
        sentClients = getJsonData(sentPath)

        # Ensure tracking files exist
        jsonCreate(deliveryPath)
        fileCreation("failed", headers=["Name", "Status"])

        # Initialize status category counters
        totalCount = 0  # Total messages checked
        failedCount = 0  # Permanent failures
        sentCount = 0  # Accepted by carrier but not yet delivered
        deliveryCount = 0  # Successfully delivered to device
        pendingCount = 0  # Awaiting carrier processing
        unknownCount = 0  # Status unavailable
        failedList = []  # Records requiring retry attention

        # Query TextBee API for each transmitted message batch
        for clients in sentClients.keys():

            # Construct batch status query endpoint using stored batch ID
            baseUrl = "https://api.textbee.dev/api/v1"
            batchID = sentClients[clients]["smsBatchId"]
            requestUrl = f"{baseUrl}/gateway/devices/{os.getenv("DEVICE_ID")}/sms-batch/{batchID}"
            headers = {
                "x-api-key": os.getenv("API_KEY"),  # Authentication token
            }

            # Execute GET request to retrieve current message status
            response = requests.get(url=requestUrl, headers=headers)
            response.raise_for_status()  # Validate HTTP success

            deliveryStatus = response.json()

            # Parse status from response and update category counters
            if deliveryStatus["data"]["messages"][0]["status"] == "sent":
                sentCount += 1  # Carrier accepted but not yet delivered

            elif deliveryStatus["data"]["messages"][0]["status"] == "failed":
                failedList.append(
                    [clients, deliveryStatus["data"]["messages"][0]["status"]]
                )
                failedCount += 1

            elif deliveryStatus["data"]["messages"][0]["status"] == "delivered":
                deliveryCount += 1

            elif deliveryStatus["data"]["messages"][0]["status"] == "pending":
                pendingCount += 1

            elif deliveryStatus["data"]["messages"][0]["status"] == "unknown":
                failedList.append(
                    [clients, deliveryStatus["data"]["messages"][0]["status"]]
                )
                unknownCount += 1

            totalCount += 1

            value = {
                "type": deliveryStatus["data"]["messages"][0]["type"],
                "status": deliveryStatus["data"]["messages"][0]["status"],
            }

            addJsonData(deliveryPath, clients, value)
            print(f"{clients} checked ✅")

        addRows("failed", failedList)  # Export failed messages for manual review

        # Compile delivery statistics with calculated success rates
        headers = ["Details", "Amount"]
        row = [
            ["Total Clients", totalCount],
            ["SMS Sent", sentCount + deliveryCount],
            ["SMS Delivered", deliveryCount],
            ["SMS Failed", failedCount],
            ["SMS Pending", pendingCount],
            ["Unknown Status", unknownCount],
            [
                "Sent Percent",
                round((((sentCount + deliveryCount) / totalCount) * 100), 2),
            ],
            ["Delivered Percent", round(((deliveryCount / totalCount) * 100), 2)],
            ["Failed Percent", round(((failedCount / totalCount) * 100), 2)],
        ]

        table = tabulate(row, headers, tablefmt="grid")
        print(table)

    except Exception as Error:
        errorDisplay(Error)


def main():
    """
    Main entry point for the TNS E-messaging CLI application.

    Handles command-line arguments and routes to appropriate functions for:
    - Displaying billing data
    - Extracting data from Excel
    - Filling message templates
    - Sending SMS messages
    - Checking delivery status
    """
    # Configure CLI argument parser
    parser = argparse.ArgumentParser(
        prog="TNS Clients' E-messaging",
        description="It accepts a custom made file and extracts data and sends required bills to clients as messages",
    )

    parser.add_argument(
        "argument",
        type=str,
        help="Action to for the program to do (display, extract, fill, send or deliver)",
    )
    parser.add_argument(  # This is for display argument
        "--filename",
        type=str,
        help="Specific file name required for the action (the exact name without extension)",
    )
    parser.add_argument(  # This is the limit for extract and display of data as well as messaging people
        "--limit",
        type=int,
        help="A number to show amount required for the earlier argument",
    )

    args = parser.parse_args()

    # Route to appropriate function based on command argument
    if args.argument == "display":

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

        displayData(f"{args.filename}.csv", headers)

    elif args.argument == "extract":

        extractData("docs/source/source_data.xlsx")

    elif args.argument == "fill":

        tempFilling(
            datetime.today(),
            f"docs/results/{args.filename}.csv",
            "docs/results/failed.csv",
        )

    elif args.argument == "send":

        sendMessage(args.limit)

    elif args.argument == "delivery":

        deliveryMessage()


if __name__ == "__main__":
    main()

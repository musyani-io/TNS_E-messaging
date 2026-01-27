"""TNS E-messaging Main Module.

This is the main entry point for the TNS (Tanzania) clients' e-messaging system.
It handles customer billing data extraction, message template filling, SMS sending
via TextBee API, and delivery status tracking.

Main functionalities:
- Display billing data in full or summary format
- Extract customer data from Excel worksheets
- Fill message templates with billing information
- Send SMS messages to customers
- Track and report message delivery status

Usage:
    python main.py display --filename "January, 2026 (1)"
    python main.py extract
    python main.py fill --filename "January, 2026 (1)"
    python main.py send --limit 10
    python main.py delivery
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
    Display customer billing data from a CSV file in either full or summary format.

    Args:
        fileName (str): Name of the CSV file to read from docs/results/ directory
        headers (list): Column headers for the table display

    Returns:
        None: Prints formatted table to console
    """
    try:
        # Initialize data path and tracking variables
        dataPath = f"docs/results/{fileName}"
        row = []
        lumoCli = 0
        chnkCli = 0
        currCharges = 0
        adjs = 0
        sum = 0

        with open(dataPath, "r") as csvFile:

            reader = csv.reader(csvFile)
            next(reader)  # Skip header row

            # Iterate through each customer record and aggregate statistics
            for rows in reader:
                row.append(rows)

                # Count clients by location (Lumo or Chanika)
                if rows[4] == "Lumo":
                    lumoCli += 1
                else:
                    chnkCli += 1

                # Sum up financial totals
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
    Extract customer billing data from an Excel worksheet and save to CSV.

    Args:
        sourcePath (str): Path to the source Excel file

        workSheet, fileName = envSetup(sourcePath)
    Returns:
        None: Creates a new CSV file with extracted data
    """
    if os.path.exists(sourcePath):
        # Setup environment: get date, worksheet reference, and output filename
        date, workSheet, fileName = envSetup(sourcePath)
        cell = workSheet["A1"]

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
        customerInfo = activeClients(
            customerInfo
        )  # Checks for validity of extracted data
        addRows(fileName, customerInfo)

        # Creation of json storage files
        jsonCreate("json_storage/data.json")
        jsonCreate("json_storage/sent.json")

    else:

        print("Error: Source File Path not Found!")
        sys.exit(1)


def sendMessage(limit):
    """
    Send SMS messages to customers using TextBee API.

    Args:
        limit (int or None): Maximum number of messages to send. If None or invalid, defaults to 40.
                            Capped at 40 max and total available recipients.

    Returns:
        None: Sends messages and logs status to JSON file
    """
    load_dotenv()
    store = "json_storage/sent.json"
    storagePath = "json_storage/data.json"

    try:
        # Configure TextBee API endpoint
        baseUrl = "https://api.textbee.dev/api/v1"
        requestUrl = f"{baseUrl}/gateway/devices/{os.getenv("DEVICE_ID")}/send-sms"

        headers = {
            "x-api-key": os.getenv("API_KEY"),
            "Content-Type": "application/json",
        }  # Authorization header and content type for API requests

        data = getJsonData(storagePath)

        names = list(data.keys())

        # Validate and normalize the limit value
        if limit is not None:
            # Enforce limit boundaries: minimum 1, maximum 40 or total recipients
            if limit > 40 or limit < 1:
                if limit > len(names):
                    limit = len(names)
                else:
                    limit = 40
        else:
            limit = 40

        # Send messages to each recipient within the limit
        for i in range(limit):

            name = names[i]
            value = data[name]
            # print(f"Name: {name}, Contact: {value["Contact"]}, \nBody: {value["Body"]}")

            # Prepare SMS payload with message body and recipient
            payload = {
                "message": value["Body"],
                # "recipients": ["+255773422381"],  # Test number - disabled in production
                "recipients": [
                    value["Contact"]
                ],  # Recipient number must be in a list format
            }

            # Send POST request to TextBee API
            response = requests.post(
                url=requestUrl, headers=headers, data=json.dumps(payload)
            )
            response.raise_for_status()
            time.sleep(1)  # Rate limiting: wait 1 second between requests

            # Store message status and metadata
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
    Check delivery status of sent SMS messages and generate delivery report.

    Queries the TextBee API for each sent message batch to determine status
    (sent, delivered, failed, pending, or unknown) and displays statistics.

    Returns:
        None: Prints formatted delivery statistics table
    """
    try:
        # Initialize storage paths and load sent messages data
        sentPath = "json_storage/sent.json"
        deliveryPath = "json_storage/delivery.json"
        sentClients = getJsonData(sentPath)

        jsonCreate(deliveryPath)
        fileCreation("failed", headers=["Name", "Status"])

        # Initialize counters for different delivery statuses
        totalCount = 0
        failedCount = 0
        sentCount = 0
        deliveryCount = 0
        pendingCount = 0
        unknownCount = 0
        failedList = []

        # Check delivery status for each client
        for clients in sentClients.keys():

            # Build API request URL with batch ID for this client
            baseUrl = "https://api.textbee.dev/api/v1"
            batchID = sentClients[clients]["smsBatchId"]
            requestUrl = f"{baseUrl}/gateway/devices/{os.getenv("DEVICE_ID")}/sms-batch/{batchID}"
            headers = {
                "x-api-key": os.getenv("API_KEY"),
            }

            # Query TextBee API for delivery status
            response = requests.get(url=requestUrl, headers=headers)
            response.raise_for_status()

            deliveryStatus = response.json()

            # Categorize message status and update counters
            if deliveryStatus["data"]["messages"][0]["status"] == "sent":
                sentCount += 1

            elif deliveryStatus["data"]["messages"][0]["status"] == "failed":
                failedList.append([clients, deliveryStatus["data"]["messages"][0]["status"]])
                failedCount += 1

            elif deliveryStatus["data"]["messages"][0]["status"] == "delivered":
                deliveryCount += 1

            elif deliveryStatus["data"]["messages"][0]["status"] == "pending":
                pendingCount += 1

            elif deliveryStatus["data"]["messages"][0]["status"] == "unknown":
                failedList.append([clients, deliveryStatus["data"]["messages"][0]["status"]])
                unknownCount += 1

            totalCount += 1

            value = {
                "type": deliveryStatus["data"]["messages"][0]["type"],
                "status": deliveryStatus["data"]["messages"][0]["status"],
            }

            addJsonData(deliveryPath, clients, value)
            print(f"{clients} checked ✅")

        addRows("failed", failedList)
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

from data_extraction import *
from tabulate import tabulate
from templates import tempFilling
from jsonSt import *
import argparse
import csv
import os
import requests
import time
import sys


def displayData(fileName, headers):
    try:

        dataPath = f"docs/results/{fileName}"
        row = []
        lumoCli = 0
        chnkCli = 0
        currCharges = 0
        adjs = 0
        sum = 0

        with open(dataPath, "r") as csvFile:

            reader = csv.reader(csvFile)
            next(reader)

            for rows in reader:
                row.append(rows)

                if rows[4] == "Lumo":
                    lumoCli += 1
                else:
                    chnkCli += 1

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
                    ["Current Bills", currCharges],
                    ["Previous debts", adjs],
                    ["Total Bills", sum],
                ]

                table = tabulate(row, headers, tablefmt="grid")
                print(table)

            else:

                print("Error: Invalid command!")
                sys.exit(1)

    except Exception as Error:
        errorDisplay(Error)


def extractData(sourcePath):

    if os.path.exists(sourcePath):

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
        addRows(fileName, customerInfo, date)

    else:

        print("Error: Source File Path not Found!")
        sys.exit(1)


def sendMessage(limit):

    load_dotenv()
    store = "json_storage/sent.json"
    storagePath = "json_storage/data.json"

    try:

        baseUrl = "https://api.textbee.dev/api/v1"
        requestUrl = f"{baseUrl}/gateway/devices/{os.getenv("DEVICE_ID")}/send-sms"

        headers = {
            "x-api-key": os.getenv("API_KEY"),
            "Content-Type": "application/json",
        }  # This is for authorization and type of data to post or get

        jsonCreate(store)
        data = getJsonData(storagePath)

        names = list(data.keys())

        # Handling the limit value
        if limit is not None:

            if limit > 40 or limit < 1:
                if limit > len(names):
                    limit = len(names)
                else:
                    limit = 40
        else:
            limit = 40

        for i in range(limit):

            name = names[i]
            value = data[name]
            # print(f"Name: {name}, Contact: {value["Contact"]}, \nBody: {value["Body"]}")

            payload = {
                "message": value["Body"],
                # "recipients": ["+255773422381"],  # This'll be changed in action, for testing purposes only.
                "recipients": [
                    value["Contact"]
                ],  # The recipient's number should be enclosed as a list
            }

            response = requests.post(
                url=requestUrl, headers=headers, data=json.dumps(payload)
            )
            response.raise_for_status()
            time.sleep(1)

            status = {
                "smsBatchId": response.json()["data"]["smsBatchId"],
                "Contact": value["Contact"],
                "Status": response.status_code,
            }
            addJsonData(store, name, status)
            delJsonData(store, storagePath)
            jsonToCsv(store, "delivered")

            # return response.json()
            print(f"Request for {name} is sent✅")

    except Exception as Error:
        errorDisplay(Error)


def main():

    # Accepting CLI arguments
    parser = argparse.ArgumentParser(
        prog="TNS Clients' E-messaging",
        description="It accepts a custom made file and extracts data and sends required bills to clients as messages",
    )

    parser.add_argument(
        "argument",
        help="Action to for the program to do (display data, extract data, search specifics or send message)",
    )
    parser.add_argument(  # This is for display argument
        "--filename",
        type=str,
        help="Specific file name (the exact name without extension)",
    )
    parser.add_argument(  # This is for search message (maybe for messaging later)
        "--name", type=str, help="Full name to search for client's information"
    )
    parser.add_argument(  # This is the limit for extract and display of data as well as messaging people
        "--limit",
        type=int,
        help="A number to show amount required for the earlier argument",
    )

    args = parser.parse_args()

    # Argument logic
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

        sourcePath = "docs/source/source_data.xlsx"
        extractData(sourcePath)

    elif args.argument == "fill":

        tempFilling(
            datetime(2025, 11, 25),
            f"docs/results/{args.filename}.csv",
            f"{args.filename}.csv",
        )

    elif args.argument == "send":

        sendMessage(args.limit)


if __name__ == "__main__":
    main()

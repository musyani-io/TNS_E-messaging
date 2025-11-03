from data_extraction import *
from tabulate import tabulate
import argparse
import csv
import os
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
        print(f"Error: {type(Error).__name__} - {Error}")
        sys.exit(1)


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
        help="Specific file name with its extension (.csv, .json)",
    )
    parser.add_argument(  # This is for search message (maybe for messaging later)
        "--name", type=str, help="Full name to search for client's information"
    )
    parser.add_argument(    # This is the limit for extract and display of data as well as messaging people
        "--limit",
        type=int,
        help="A number to show amount required for the earlier argument"
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

        displayData(args.filename, headers)

    elif args.argument == "extract":

        sourcePath = "docs/source/source_data.xlsx"
        extractData(sourcePath)


if __name__ == "__main__":
    main()

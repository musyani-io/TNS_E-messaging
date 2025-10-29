from tabulate import tabulate
import argparse
import csv
import os
import sys


def displayData(fileName, headers):
    try:

        parameter = input("What should be displayed? (full or summary): ")
        dataPath = f"docs/results/{fileName}"
        data = []
        row = []
        sum = 0

        with open(dataPath, "r") as csvFile:

            reader = csv.reader(csvFile)
            next(reader)
            print("")

            for rows in reader:
                row.append(rows)
                sum += int(rows[8])

            if parameter == "full":

                table = tabulate(row, headers, tablefmt="grid")
                print(table)

            elif parameter == "summary":

                clientNum = len(row)
                headers = ["Details", "Amount"]
                row = [
                    ["Total clients: ", clientNum],
                    ["Total Bills: ", sum],
                ]

                table = tabulate(row, headers, tablefmt="grid")
                print(table)

    except Exception as Error:
        print(f"Error: {type(Error).__name__} - {Error}")
        sys.exit(1)


def main():

    # Accepting CLI arguments
    parser = argparse.ArgumentParser(
        prog="TNS Clients' E-messaging",
        description="It accepts a custom made file and extracts data and sends required bills to clients as messages",
    )

    parser.add_argument(
        "argument",
        help="Action to for the program to do (display data, extract data, filter data or send message)",
    )
    parser.add_argument(
        "--filename",
        type=str,
        help="Specific file name with its extension (.csv, .json)",
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


if __name__ == "__main__":
    main()

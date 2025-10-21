from miscallenous import *
import openpyxl
import os
import sys
from datetime import datetime


def envSetup(sourcePath):
    # Returns the required worksheet to work at that time!

    date = datetime(2024, 9, 3)  # Dummy date for configuration, will be erased later
    # date = datetime.today()  # This will be enable on final testing and usage
    month = dateTime_dict[date.month]

    try:

        workbook = openpyxl.load_workbook(sourcePath, data_only=True)
        workSheet = workbook[f"Accounts for {dateTime_dict[date.month]}, {date.year}"]
        return workSheet

    except Exception as Error:
        print(f"Error: {type(Error).__name__} - {Error}")
        sys.exit(1)


def extractFromBox(cell):

    def jumpTo(row, col):
        return cell.offset(row=row, column=col)

    # Extract communication type, name and telephone
    commCell = jumpTo(0, 3)
    nameCell = jumpTo(1, 1)
    numCell = jumpTo(1, 3)
    numCell.value = localToInt(numCell.value)

    # Extract reading date
    readingDate = jumpTo(2, 4)
    readingDate.value = datetime.strftime(readingDate.value, "%d-%b-%Y")

    # Extract amount in liters used, net charge and adjustments
    literUsage = jumpTo(5, 4)
    netCharge = jumpTo(6, 4)
    adjustments = jumpTo(7, 4)

    # Extract final bill
    bill = jumpTo(11, 1)

    return (
        readingDate.value,
        nameCell.value,
        numCell.value,
        commCell.value,
        round(literUsage.value, 1),
        int(netCharge.value),
        (adjustments.value),
        bill.value,
    )


def iterateOverBoxes(startCell):
    # As the name, goes over a fixed increment to collect data to other boxes

    usedCell = startCell
    vertCustomers = 2
    customerInfo = []
    rowIncr = 14
    colIncr = 6
    count = 0

    while vertCustomers > 0:  # Iterate going downwards

        horzCustomers = 3
        while horzCustomers > 0:  # Iterate sideways

            customerInfo.append(extractFromBox(usedCell))

            usedCell = usedCell.offset(row=0, column=colIncr)
            horzCustomers -= 1

        count += 1
        usedCell = startCell
        usedCell = usedCell.offset(row=(count * rowIncr), column=0)
        vertCustomers -= 1

    return customerInfo


if __name__ == "__main__":

    sourceFilePath = "docs/source/source_data.xlsx"

    if os.path.exists(sourceFilePath):

        workSheet = envSetup(sourceFilePath)

        startCell = workSheet["A1"]
        print(iterateOverBoxes(startCell))

    else:
        print("Invalid path provided!")
        sys.exit(1)

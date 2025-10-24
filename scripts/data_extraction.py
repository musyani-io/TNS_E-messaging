from miscallenous import *
from datetime import datetime
from extracted_csv import *
import openpyxl
import os
import sys


def envSetup(sourcePath):
    # Returns the required worksheet to work at that time!

    date = datetime(2024, 8, 22)  # Dummy date for configuration, will be erased later
    # date = datetime.today()  # This will be enable on final testing and usage

    try:

        workbook = openpyxl.load_workbook(sourcePath, data_only=True)
        workSheet = workbook[f"Accounts for {dateTime_dict[date.month]}, {date.year}"]
        return workSheet, f"{dateTime_dict[date.month]}, {date.year}"

    except Exception as Error:
        print(f"Error: {type(Error).__name__} - {Error}")
        sys.exit(1)


def extractFromBox(cell):

    def jumpTo(row, col):
        return cell.offset(row=row, column=col)
    
    def noneReturn(value, exceptionValue):
        return exceptionValue if value is None else value

    # Extract communication type, name and telephone
    commCell = jumpTo(0, 3)
    nameCell = jumpTo(1, 1)
    numCell = jumpTo(1, 3)
    numCell.value = localToInt(numCell.value)

    # Extract reading date
    readingDate = jumpTo(2, 4)
    readingDate.value = noneReturn(readingDate.value, datetime(2000, 1, 1))
    readingDate.value = datetime.strftime(readingDate.value, "%d-%b-%Y")

    # Extract amount in liters used, net charge and adjustments
    literUsage = jumpTo(5, 4)
    netCharge = jumpTo(6, 4)
    adjustments = jumpTo(7, 4)

    # Extract final bill
    bill = jumpTo(11, 1)

    # Extract customer's color (location varied)
    topColor = cell.border.top.color
    color = topColor.index if topColor else None
    if color is None:
        location = "Lumo"
    else:
        location = "Chanika"

    return (
        readingDate.value,
        nameCell.value,
        numCell.value,
        commCell.value,
        location,
        round(noneReturn(literUsage.value, 0), 1),
        int(noneReturn(netCharge.value, 0)),
        0 if adjustments.value is None else adjustments.value,
        noneReturn(bill.value, 0),
    )



def iterateOverBoxes(startCell):
    # As the name, goes over a fixed increment to collect data to other boxes

    usedCell = startCell
    vertCustomers = 8
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

        workSheet, fileName = envSetup(sourceFilePath)  # Require sheet given

        startCell = workSheet["A1"]
        customerInfo = iterateOverBoxes(startCell)  # Iterated over box to collect data

        fileCreation(fileName)
        addCsvData(fileName, customerInfo)

    else:
        print("Invalid path provided!")
        sys.exit(1)

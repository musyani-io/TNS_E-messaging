from miscallenous import *
from datetime import datetime
from extracted_csv import *
import openpyxl
import os
import sys


def envSetup(sourcePath):
    # Returns the required worksheet to work at that time!

    date = datetime(2024, 8, 22)  # Dummy date for configuration, will be erased later
    # date = datetime.today()  # This will be enabled on final testing and usage

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

    # Extract date
    readingDate = jumpTo(1, 4)
    # readingDate.value = noneReturn(readingDate.value, datetime(2000, 1, 1))

    # Extract name and contact info
    name = jumpTo(0, 1)
    comm = jumpTo(0, 3)
    comm.value = localToInt(comm.value)

    # Extract communication application and location
    commApp = jumpTo(-1, 3) 
    colorBox = jumpTo(-1, 0)
    topColor = colorBox.border.top.color
    color = topColor.index if topColor else None
    if color is None:
        location = "Lumo"
    else:
        location = "Chanika"

    # Extract liters used and net charge
    literUsed = jumpTo(4, 4)
    netCharge = jumpTo(5, 4)

    # Extract adjustments and final bill
    adjustments = jumpTo(6, 4)
    finalBill = jumpTo(10, 1)

    return [
        readingDate.value,
        name.value,
        comm.value,
        commApp.value,
        location,
        round(noneReturn(literUsed.value, 0), 1),
        int(noneReturn(netCharge.value, 0)),
        int(noneReturn(adjustments.value, 0)),
        int(noneReturn(finalBill.value, 0)),
    ]


def iterateOnBoxes(cell):

    startCell = cell
    col = 0
    customerInfo = []
    try:
        while col < 3:
            
            rows = 786  # No. of iteration to cover all boxes

            while rows > 0:

                if cell.value == "Name/Tel:":  # Box with 'Name/Tel:' is the starting point
                    print(extractFromBox(cell))
                    customerInfo.append(extractFromBox(cell))

                cell = cell.offset(row=1, column=0)
                rows -= 1

            col += 1
            cell = startCell
            cell = cell.offset(row=0, column=(6 * col))

        return customerInfo

    except Exception as Error:
        print(f"Error: {type(Error).__name__} - {Error}")
        sys.exit(1)


if __name__ == "__main__":

    sourceFilePath = "docs/source/source_data.xlsx"

    if os.path.exists(sourceFilePath):

        workSheet, fileName = envSetup(sourceFilePath)  # Require sheet given

        startCell = workSheet["A1"]

        customerInfo = iterateOnBoxes(startCell)
        print(customerInfo, end="\n")
        # fileCreation(fileName)
        # addCsvData(fileName, customerInfo)

    else:
        print("Invalid path provided!")
        sys.exit(1)

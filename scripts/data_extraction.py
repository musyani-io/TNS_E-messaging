from miscallenous import *
from datetime import datetime
from extracted_csv import *
import openpyxl
import os
import sys


def envSetup(sourcePath):
    # Returns the required worksheet to work at that time!

    date = datetime(2024, 6, 22)  # Dummy date for configuration, will be erased later
    # date = datetime.today()  # This will be enabled on final testing and usage

    try:

        workbook = openpyxl.load_workbook(sourcePath, data_only=True)
        workSheet = workbook[f"Accounts for {dateTime_dict[date.month]}, {date.year}"]
        return (
            date.strftime("%d-%b-%Y"),
            workSheet,
            f"{dateTime_dict[date.month]}, {date.year}",
        )

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
    dateStr = readingDate.value.strftime("%d-%b-%Y")

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
        dateStr,
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
        while col < 3:  # No. of iterations to cover all boxes (horizontally)

            rows = 0  # No. of iterations to cover all boxes (vertically)

            while rows < 786:

                if type(cell).__name__ == "MergedCell":
                    rows += 1

                if (
                    cell.value == "Name/Tel:"
                ):  # Box with 'Name/Tel:' is the starting point
                    customerInfo.append(extractFromBox(cell))

                cell = startCell
                cell = cell.offset(row=rows, column=(6 * col))
                rows += 1

            col += 1

        return customerInfo

    except Exception as Error:
        print(f"Error: {type(Error).__name__} - {Error}")
        sys.exit(1)


if __name__ == "__main__":

    even = [2, 4, 6, 8]
    prime = [2, 3, 5, 7]

    list1 = set(even)
    list2 = set(prime)

    print(list1 - list2)  # What is in list1 but not in list2

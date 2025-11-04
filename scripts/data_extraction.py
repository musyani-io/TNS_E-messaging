from miscallenous import *
from datetime import datetime
from extracted_csv import *
import openpyxl

def envSetup(sourcePath):
    # Returns the required worksheet to work at that time!

    date = datetime(2024, 1, 22)  # Dummy date for configuration, will be erased later
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
        errorDisplay(Error)


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
        comm.value,    # If the number isn't provided, messages are sent to owner himself
        noneReturn(commApp.value, "s m s"),
        location,
        str(round(noneReturn(literUsed.value, 0), 1)),
        str(int(noneReturn(netCharge.value, 0))),
        str(int(noneReturn(adjustments.value, 0))),
        str(int(noneReturn(finalBill.value, 0))),
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
        errorDisplay(Error)


if __name__ == "__main__":

    pass

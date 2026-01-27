"""Data Extraction Module.

Handles extraction of customer billing data from Excel worksheets.
Parses structured customer information from formatted Excel boxes including:
- Customer names and contact information
- Communication app preferences
- Water usage (liters)
- Billing amounts and adjustments
- Location identification (Lumo/Chanika based on cell formatting)

The module navigates through Excel cells in a grid pattern to locate and
extract data from each customer's box using cell offset navigation.
"""

from miscallenous import *
from datetime import datetime
from extracted_csv import *
import openpyxl


def envSetup(sourcePath):
    """
    Setup the Excel workbook environment and extract date/worksheet information.

    Args:
        sourcePath (str): Path to the source Excel file

    Returns:
        tuple: (formatted_date, worksheet_object, output_filename)
            - formatted_date: String in format "DD-Mon-YYYY"
            - worksheet_object: openpyxl worksheet reference
            - output_filename: String like "Month, Year"
    """
    # Configure reading date (currently set to dummy date for testing)
    date = datetime(2025, 12, 20)  # Dummy date for configuration, will be erased later
    # date = datetime.today()  # This will be enabled on final testing and usage

    try:

        workbook = openpyxl.load_workbook(sourcePath, data_only=True)
        workSheet = workbook["December '25"]
        return (
            date.strftime("%d-%b-%Y"),
            workSheet,
            f"{dateTime_dict[date.month]}, {date.year}",
        )

    except Exception as Error:
        errorDisplay(Error)


def extractFromBox(cell):
    """
    Extract customer billing information from a single Excel box/cell region.

    Parses structured data from Excel cells including customer name, contact info,
    communication app, location (Lumo/Chanika based on border color), usage metrics,
    and billing amounts.

    Args:
        cell: openpyxl cell object representing the top-left corner of the data box

    Returns:
        list: [reading_date, name, contact, comm_app, location, liters_used,
               net_charge, adjustments, final_bill]
    """

    def jumpTo(row, col):
        """Helper function to navigate to offset cells."""
        return cell.offset(row=row, column=col)

    def noneReturn(value, exceptionValue):
        """Helper function to provide default values for None."""
        return exceptionValue if value is None else value

    # Extract and format reading date
    readingDate = jumpTo(1, 4)
    if isinstance(readingDate.value, str):  # Handle invalid string dates
        readingDate.value = None

    readingDate.value = noneReturn(readingDate.value, datetime(2000, 1, 1))
    dateStr = readingDate.value.strftime("%d-%b-%Y")

    # Extract customer name and contact number
    name = jumpTo(0, 1)
    comm = jumpTo(-1, 1)
    if comm.value is None:
        comm = jumpTo(0, 3)  # Try alternate cell if primary is empty

    comm.value = localToInt(comm.value)  # Convert to international format

    # Extract communication app preference and determine location by border color
    commApp = jumpTo(-1, 3)
    colorBox = jumpTo(-1, 0)
    topColor = colorBox.border.top.color
    color = topColor.index if topColor else None
    # Location determined by cell border color: No color = Lumo, Color = Chanika
    if color is None:
        location = "Lumo"
    else:
        location = "Chanika"

    # Extract usage and billing information
    literUsed = jumpTo(4, 4)
    netCharge = jumpTo(5, 4)

    # Extract adjustments (previous debts) and compute final bill
    adjustments = jumpTo(6, 4)
    finalBill = jumpTo(10, 1)

    # Return all extracted data as a formatted list
    return [
        dateStr,
        name.value,
        comm.value,  # If number isn't provided, owner's number is used
        noneReturn(commApp.value, "s m s"),
        location,
        str(round(noneReturn(literUsed.value, 0), 1)),
        str(int(noneReturn(netCharge.value, 0))),
        str(int(noneReturn(adjustments.value, 0))),
        str(int(noneReturn(finalBill.value, 0))),
    ]


def iterateOnBoxes(cell):
    """
    Iterate through all customer data boxes in the Excel worksheet.

    Scans the worksheet in a grid pattern (3 columns x ~910 rows) to locate
    and extract data from each customer box, identified by the "Name/Tel:" marker.

    Args:
        cell: Starting cell (typically A1) for the iteration

    Returns:
        list: List of customer information lists, each containing billing details
    """
    startCell = cell
    col = 0
    customerInfo = []
    try:
        # Iterate through 3 columns of customer boxes
        while col < 3:  # No. of iterations to cover all boxes (horizontally)

            rows = 0  # No. of iterations to cover all boxes (vertically)

            while rows < 910:

                if type(cell).__name__ == "MergedCell":  # Skip merged cells
                    rows += 1

                # Identify customer data box by "Name/Tel:" marker
                if (
                    isinstance(cell.value, str) and "Name/Tel:" in cell.value
                ):  # Box with 'Name/Tel:' is the starting point
                    customerInfo.append(extractFromBox(cell))

                # Navigate to next cell in the grid
                cell = startCell
                cell = cell.offset(row=rows, column=(6 * col))  # 6 cells per box width
                rows += 1

            col += 1

        return customerInfo

    except Exception as Error:
        errorDisplay(Error)


if __name__ == "__main__":

    pass

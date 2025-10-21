from miscallenous import *
import openpyxl
import os
import sys
from datetime import datetime


def envSetup(sourcePath):
    # Returns the required worksheet to work at that time!

    date = datetime(2024, 1, 3) # Dummy date for configuration, will be erased later
    # date = datetime.today()  # This will be enable on final testing and usage
    month = dateTime_dict[date.month]

    try:

        workbook = openpyxl.load_workbook(sourcePath, data_only=True)
        workSheet = workbook[f"Accounts for {dateTime_dict[date.month]}, {date.year}"]
        return workSheet

    except Exception as Error:
        print(f"Error: {type(Error).__name__} - {Error}")
        sys.exit(1)


def extractFromBox():
    pass


if __name__ == "__main__":

    sourceFilePath = "docs/source/source_data.xlsx"

    if os.path.exists(sourceFilePath):

        print(envSetup(sourceFilePath))

    else:
        print("Invalid path provided!")
        sys.exit(1)

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
    

def iterateOnBoxes(cell):

    rows = 50
    customerInfo = []
    try:

        while rows > 0:
            
            customerInfo.append(cell)
            cell = cell.offset(row=1, column=0)
            rows -= 1

        return customerInfo

    except Exception as Error:
        print(f"Error: {type(Error).__name__} - {Error}")
    

if __name__ == "__main__":

    sourceFilePath = "docs/source/source_data.xlsx"

    if os.path.exists(sourceFilePath):

        workSheet, fileName = envSetup(sourceFilePath)  # Require sheet given

        startCell = workSheet["A1"]
        
        print(iterateOnBoxes(startCell))
        # fileCreation(fileName)
        # addCsvData(fileName, customerInfo)

    else:
        print("Invalid path provided!")
        sys.exit(1)

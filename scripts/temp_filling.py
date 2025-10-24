import csv
import sys

def fillTemp(tempPath, var):
    # Read the file first
    try: 
        with open(tempPath, "r") as temp:
            file = temp.read()
            filled = file.format(**var)
            print(filled)

    except Exception as Error:
        print(f"Error: {type(Error).__name__} - {Error}")

def readCsv(fileName):

    try:
        filePath = f"docs/results/{fileName}.csv"

        with open(filePath, "r") as csvFile:
            reader = csv.reader(csvFile)

            next(reader)
            rows = []
            for row in reader:
                rows.append(row)

            print(rows)

    except Exception as Error:
        print(f"Error: {type(Error).__name__} - {Error}")
        sys.exit(1)


if __name__ == "__main__":
    readCsv("Aug, 2024")
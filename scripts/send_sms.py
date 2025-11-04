from extracted_csv import *


def dataExtraction(filePath, count):
    # Data to be extracted for

    try:

        with open(filePath, "r") as csvFile:

            reader = csv.reader(csvFile)

            presentData = []
            next(reader)
            for rows in reader:
                presentData.append(rows)

            if count > 0 and count <= len(presentData):
                pass
            else:
                count = None

            extractedData = []
            if count:
                for rows in presentData:
                    if count > 0:
                        extractedData.append(rows)
                        count -= 1
            else:
                print("Invalid limit entered!")

            return extractedData

    except Exception as Error:
        errorDisplay(Error)


if __name__ == "__main__":

    print(dataExtraction("docs/results/Feb, 2024.csv", 5))

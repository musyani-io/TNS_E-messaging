import csv
import sys
from send_sms import send_sms
from datetime import datetime, timedelta


def fillTemp(tempPath, var):
    # Read the file first
    try:
        with open(tempPath, "r") as temp:
            file = temp.read()  # Reading a normal file
            filledTemp = file.format(**var)

            return filledTemp

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

                startDate = datetime.strptime(row[0], "%d-%b-%Y")
                newDate = datetime.strftime((startDate + timedelta(7)), "%d-%m-%Y")

                var = {  # Dictionary for variables in message templates.
                    "Month, year": fileName,
                    "Customer Name": row[1],
                    "Liters Used": row[5],
                    "Net Charge": row[6],
                    "Adjustments": row[7],
                    "Final Bill": row[8],
                    "Deadline Date": newDate,
                }

                tempPath = f"message_templates/{row[4]}/smart_text.txt"

                # print (fillTemp(tempPath, var), row[2]) # row[2] is for contacts
                try:

                    send_sms(fillTemp(tempPath, var), "+255773422381")
                    print(f"Sent successfully to BlaaBlaa")
                
                except:
                    print(f"Error: {type(Error).__name__} - {Error}")
                    sys.exit(1)

    except Exception as Error:
        print(f"Error: {type(Error).__name__} - {Error}")
        sys.exit(1)


if __name__ == "__main__":
    readCsv("Aug, 2024")

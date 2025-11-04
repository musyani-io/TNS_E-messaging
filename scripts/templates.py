from extracted_csv import *
from dotenv import load_dotenv
from datetime import datetime, timedelta
import os

load_dotenv()

def tempFilling(filePath, fileName):
    # Data to be extracted for

    try:

        with open(filePath, "r") as csvFile:

            reader = csv.reader(csvFile)

            presentData = []
            next(reader)
            for row in reader:
                
                presentData.append(row)
                
                filePath = f"message_templates/{row[4]}/smart_text.txt"
                with open(filePath, "r") as f:

                    file = f.read()

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
                        "AZAMPESA": os.getenv("AZAMPESA"),
                        "LIPA_NAMBA": os.getenv("LIPA_NAMBA"),
                        "TigoPesa": os.getenv("TIGOPESA")
                    }
                    filledTemp = file.format(**var)

            return filledTemp
            
    except Exception as Error:
        errorDisplay(Error)

if __name__ == "__main__":

    print(tempFilling("docs/results/Feb, 2024.csv", "Feb-2024"))

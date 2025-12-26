from dotenv import load_dotenv
import os
import sys

load_dotenv()

def localToInt(localNumber):

    if localNumber is None:
        intNumber = os.getenv("OWNER_NO")

    else:
        localNumber = str(localNumber)
        localNumber = localNumber.replace(" ", "")
        intNumber = "+255" + localNumber[1:]

    return intNumber


def errorDisplay(error):
    # Function to display the exact location of the error

    _p1, _p2, exc_traceback = sys.exc_info()  # Returns a tuple of the error info

    if exc_traceback:

        print(
            f"Error at file: {exc_traceback.tb_frame.f_code.co_filename}, line: {exc_traceback.tb_lineno}"
        )
        print(f"Error details: {type(error).__name__} - {error}")
        sys.exit(1)

    else:
        sys.exit(0)

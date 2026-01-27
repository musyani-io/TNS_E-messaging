"""Miscellaneous Utility Functions Module.

Provides helper functions and constants used across the TNS E-messaging system.

Features:
- Phone number format conversion (local to international)
- Enhanced error display with traceback information
- Date/time constants and mappings
- Special cases configuration
"""

from dotenv import load_dotenv
import os
import sys

load_dotenv()

dateTime_dict = {
    1: "Jan",
    2: "Feb",
    3: "Mar",
    4: "Apr",
    5: "May",
    6: "June",
    7: "July",
    8: "Aug",
    9: "Sept",
    10: "Oct",
    11: "Nov",
    12: "Dec",
}

specialCases = [
    "Little Doves' Centre",  # Complicated computations
    # "Boniface Kirundwa", # Disconnected client
]


def localToInt(localNumber):
    """
    Convert local Tanzanian phone number format to international format.

    Transforms numbers from local format (e.g., 0773422381) to international
    format (e.g., +255773422381). If no number provided, returns owner's number.

    Args:
        localNumber (str or int or None): Local phone number or None

    Returns:
        str: Phone number in international format (+255...)
    """
    if localNumber is None:
        # Use owner's number as fallback if no customer number provided
        intNumber = os.getenv("OWNER_NO")

    else:
        # Convert local format to international: remove spaces and replace leading 0 with +255
        localNumber = str(localNumber)
        localNumber = localNumber.replace(" ", "")
        intNumber = "+255" + localNumber[1:]

    return intNumber


def errorDisplay(error):
    """
    Display detailed error information including file location and line number.

    Extracts traceback information to show exactly where an error occurred,
    then exits the program.

    Args:
        error (Exception): The exception object that was caught

    Returns:
        None: Prints error details and exits program with status code 1
    """
    _p1, _p2, exc_traceback = sys.exc_info()  # Returns a tuple of the error info

    if exc_traceback:
        # Extract and display file path, line number, and error details
        print(
            f"Error at file: {exc_traceback.tb_frame.f_code.co_filename}, line: {exc_traceback.tb_lineno}"
        )
        print(f"Error details: {type(error).__name__} - {error}")
        sys.exit(1)  # Exit with error code

    else:
        sys.exit(0)

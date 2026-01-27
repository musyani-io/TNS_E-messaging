"""Utility Functions and Shared Constants Module.

Provides cross-cutting concerns used throughout the TNS E-messaging system,
including phone number normalization, enhanced error reporting, and configuration constants.

Functions:
    * localToInt(): Convert Tanzanian phone numbers from local to E.164 international format
    * errorDisplay(): Enhanced exception handler with file/line traceback information

Shared Configuration:
    No longer includes dateTime_dict or specialCases (removed in current version)

Phone Number Format Transformation:
    Input:  "0773422381" (Tanzanian local format)
    Output: "+255773422381" (E.164 international format)

    Format Specification (E.164):
    - Country code: +255 (Tanzania)
    - Subscriber number: 9 digits (replacing leading 0)
    - No spaces or punctuation in final output

Error Handling Philosophy:
    System uses fail-fast approach with detailed error reporting to facilitate debugging.
    All exceptions are caught at function boundaries and passed to errorDisplay() for
    consistent formatting and program termination.
"""

from dotenv import load_dotenv
import os
import sys

load_dotenv()


def localToInt(localNumber):
    """
    Normalize Tanzanian phone numbers to E.164 international format.

    Converts local phone number formats (0XXXXXXXXX) to internationally dialable
    format (+255XXXXXXXXX) required by SMS gateway APIs. Provides fallback to
    system owner's number for missing customer contacts.

    Args:
        localNumber (str | int | None): Phone number in local format:
            - str: "0773422381" or "0773 422 381" (spaces allowed)
            - int: 773422381 (leading zero may be missing)
            - None: Triggers fallback to owner number

    Returns:
        str: E.164 formatted international number "+255XXXXXXXXX"
            - Always includes + prefix
            - Always starts with 255 (Tanzania country code)
            - No spaces or formatting characters

    Environment Variables:
        OWNER_NO (str): Fallback number from .env file, used when localNumber is None

    Examples:
        >>> localToInt("0773422381")
        "+255773422381"
        >>> localToInt("0773 422 381")
        "+255773422381"
        >>> localToInt(None)  # Assumes OWNER_NO="+255700000000"
        "+255700000000"

    Note:
        Does not validate number length or format. Assumes all inputs follow
        Tanzanian mobile numbering plan (9 digits after country code).
    """
    if localNumber is None:
        # Fallback strategy: use system owner's contact when customer number unavailable
        intNumber = os.getenv("OWNER_NO")

    else:
        # Normalize to string and strip whitespace, then apply E.164 transformation
        localNumber = str(localNumber)
        localNumber = localNumber.replace(" ", "")  # Remove formatting spaces
        intNumber = "+255" + localNumber[1:]  # Replace leading 0 with +255

    return intNumber


def errorDisplay(error):
    """
    Enhanced exception handler with traceback information for debugging.

    Intercepts exceptions at module boundaries to provide detailed error context
    including exact file location and line number where exception originated.
    After displaying error details, terminates program with appropriate exit code.

    Args:
        error (Exception): Caught exception object from try-except block

    Returns:
        Never returns: Always calls sys.exit()

    Exit Codes:
        * 1: Error occurred (traceback available)
        * 0: Clean exit (no traceback, unlikely in practice)

    Output Format:
        Error at file: /path/to/file.py, line: 42
        Error details: ValueError - invalid literal for int() with base 10

    Usage Pattern:
        >>> try:
        ...     risky_operation()
        ... except Exception as Error:
        ...     errorDisplay(Error)  # Never returns

    Design Philosophy:
        Fail-fast approach prioritizes rapid error detection and clear diagnostics
        over graceful degradation. All errors are considered fatal in this system.
    """
    _p1, _p2, exc_traceback = sys.exc_info()  # Unpack exception info tuple

    if exc_traceback:
        # Extract traceback details and format for console output
        print(
            f"Error at file: {exc_traceback.tb_frame.f_code.co_filename}, "
            f"line: {exc_traceback.tb_lineno}"
        )
        print(f"Error details: {type(error).__name__} - {error}")
        sys.exit(1)  # Terminate with error status

    else:
        # Edge case: exception info unavailable (should rarely occur)
        sys.exit(0)

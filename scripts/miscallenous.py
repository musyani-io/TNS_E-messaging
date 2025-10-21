# This file is mainly here for custom short form of words used in the documents

dateTime_dict = {
    1: "Jan",
    2: "Feb",
    3: "March",
    4: "April",
    5: "May",
    6: "June",
    7: "July",
    8: "Aug",
    9: "Sept",
    10: "Oct",
    11: "Nov",
    12: "Dec",
}

def localToInt(localNumber):

    localNumber = localNumber.replace(" ", "")
    intNumber = "+255" + localNumber[1:]

    return intNumber

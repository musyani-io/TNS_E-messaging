from miscallenous import errorDisplay
import json
import os

def jsonCreate(store):
    # Creates the JSON file and pushes an empty dictionary into it.

    if not os.path.exists(store):
        try:
            with open(store, "x"):
                pass
            #   print("File created✅")

        except Exception as Error:
            errorDisplay(Error)

    # if os.stat(store).st_size == 0:

    #     try:
    #         with open(store, "w") as file:

    #             tasks = {}
    #             json.dump(tasks, file, indent=4)
    #             # print("File saved in JSON✅")

        except Exception as Error:
            errorDisplay(Error)

def dictDataToJson(store, data):  # The data is the python dictionary
    # Converts the list to JSON for storage

    try:
        with open(store, "w") as file:

            json.dump(data, file, indent=4)

    except Exception as Error:
        errorDisplay(Error)
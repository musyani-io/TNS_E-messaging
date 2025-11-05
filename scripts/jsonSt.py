from miscallenous import errorDisplay
import json
import os

storagePath = "json_storage/data.json"


def jsonCreate():

    storagePath = "json_storage/data.json"
    try:

        if not os.path.exists(storagePath):
            # Create a json file
            with open(storagePath, "x") as store:

                task = {}
                json.dump(task, store, indent=4)
                print("Storage file created✅")

    except Exception as Error:
        errorDisplay(Error)


def getJsonData():
    # The 'data' should be written in a dictionary format

    try:

        with open(storagePath, "r") as store:

            presentData = json.load(store)

            return presentData

    except Exception as Error:
        errorDisplay(Error)


def addJsonData(key, value):

    try:

        presentData = getJsonData()
        with open(storagePath, "w") as store:

            presentData[key] = value
            json.dump(presentData, store, indent=4)

    except Exception as Error:
        errorDisplay(Error)


if __name__ == "__main__":

    pass

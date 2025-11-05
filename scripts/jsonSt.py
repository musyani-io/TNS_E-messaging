from miscallenous import errorDisplay
import json
import os


def jsonCreate(storagePath):

    try:

        if not os.path.exists(storagePath):
            # Create a json file
            with open(storagePath, "x") as store:

                task = {}
                json.dump(task, store, indent=4)
                print("Storage file created✅")

    except Exception as Error:
        errorDisplay(Error)


def getJsonData(storagePath):
    # The 'data' should be written in a dictionary format

    try:

        with open(storagePath, "r") as store:

            presentData = json.load(store)

            return presentData

    except Exception as Error:
        errorDisplay(Error)


def addJsonData(storagePath, key, value):

    try:

        presentData = getJsonData(storagePath)
        with open(storagePath, "w") as store:

            presentData[key] = value
            json.dump(presentData, store, indent=4)

    except Exception as Error:
        errorDisplay(Error)


if __name__ == "__main__":

    pass

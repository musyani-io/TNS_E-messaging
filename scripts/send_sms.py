from dotenv import load_dotenv
import os
import requests
import sys
import json

load_dotenv()
apiKey = os.getenv("API_KEY")
deviceId = os.getenv("DEVICE_ID")


def send_sms(message, phoneNumber):

    baseUrl = "https://api.textbee.dev/api/v1"
    requestUrl = f"{baseUrl}/gateway/devices/{deviceId}/send-sms"

    headers = {"x-api-key": apiKey, "Content-Type": "application/json"}

    payload = {
        "message": message,
        "recipients": [phoneNumber],  # The contacts should be a list type shit
    }

    try:

        response = requests.post(
            url=requestUrl, headers=headers, data=json.dumps(payload)
        )
        response.raise_for_status()
        return response.json()

    except Exception as Error:
        print(f"Status code: {response.status_code}, Error: {type.__name__} - {Error}")
        sys.exit(1)

if __name__ == "__main__":

    phoneNumber = "+255773422381"
    if send_sms("Hello", phoneNumber):
        print(f"Sent to {phoneNumber}✅")

    else:
        print("Not succesful")
# http_client.py – Send data to FastAPI
import urequests
from secrets import SECRETS
from config import load_config

config = load_config()
BASE_URL = SECRETS["api_url"]
API_KEY = SECRETS["api_key"]
DEVICE_NAME = config["device_name"]

HEADERS = {
    "Content-Type": "application/json",
    "x-api-key": API_KEY
}

def post_moisture(value, voltage):
    try:
        payload = {
            "name": DEVICE_NAME,
            "value": value,
            "voltage": voltage
        }
        res = urequests.post(BASE_URL + "/plants/moisture", json=payload, headers=HEADERS)
        print("Moisture POST status:", res.status_code)
        res.close()
    except Exception as e:
        print("Moisture POST failed:", e)

def post_pump_event():
    try:
        payload = { "name": DEVICE_NAME }
        res = urequests.post(BASE_URL + "/plants/watering", json=payload, headers=HEADERS)
        print("Pump POST status:", res.status_code)
        res.close()
    except Exception as e:
        print("Pump POST failed:", e)

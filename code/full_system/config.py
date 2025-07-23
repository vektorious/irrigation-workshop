# config.py – Default fallback values
import os

CONFIG = {
"device_name": "Test Setup",
    "mode": "test",  # "test" or "prod"
    "max_voltage": 3.0,  # adjust to the highest voltage measured e.g. while the sensor is in the air or in very dry soil
    "min_voltage": 0.5,  # adjust to the lowest voltage measured e.g. while the sensor is in water or in very moist soil
    "moisture_threshold": 30.0,  # %
    "pump_duration": 10,  # seconds
    "measure_interval": 5,  # hours, used if schedule_mode is "interval"
    "schedule_mode": "interval",  # "interval" or "times"
    "measure_times": ["08:00", "12:00", "16:00", "20:00"]  # up to 4 times
}

# Load config from config.json if it exists
def load_config():
    try:
        if "config.json" in os.listdir():
            with open("config.json", "r") as f:
                data = ujson.load(f)
                CONFIG.update(data)
                print("Loaded config.json")
    except Exception as e:
        print("Failed to load config.json:", e)
    return CONFIG

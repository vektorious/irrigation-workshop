# main.py – Pico main loop
import machine
import time
from config import load_config
from secrets import SECRETS
from http_client import post_moisture, post_pump_event
import neopixel

# === Setup ===
config = load_config()

DEVICE_NAME = config["device_name"]
MODE = config["mode"]
THRESHOLD = config["moisture_threshold"]
PUMP_DURATION = config["pump_duration"]
INTERVAL = config["measure_interval"]
MAX_VOLTAGE = config.get("max_voltage", 3.0)
MIN_VOLTAGE = config.get("min_voltage", 0.5)
LOW_THRESHOLD = config.get("low_threshold", 30)
MEDIUM_THRESHOLD = config.get("medium_threshold", 50)
LED_BRIGHTNESS = config.get("led_brightness", 1.0)  # scale 0.0–1.0

adc = machine.ADC(26)
pump = machine.Pin(15, machine.Pin.OUT)
pump.value(0)

np = neopixel.NeoPixel(machine.Pin(1), 10)  # GP1, 10 LEDs

# === WiFi Setup ===
import network
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(SECRETS["wifi_ssid"], SECRETS["wifi_password"])

print("Connecting to WiFi...")
while not wlan.isconnected():
    time.sleep(0.5)
print("Connected, IP:", wlan.ifconfig()[0])

# === Helper Functions ===
def read_moisture():
    voltage = adc.read_u16() / 65535 * 3.3
    voltage = max(min(voltage, MAX_VOLTAGE), MIN_VOLTAGE)
    percent = (MAX_VOLTAGE - voltage) / (MAX_VOLTAGE - MIN_VOLTAGE) * 100
    return round(percent, 1), round(voltage, 2)

def run_pump():
    print("Pump ON")
    pump.value(1)
    time.sleep(PUMP_DURATION)
    pump.value(0)
    print("Pump OFF")
    post_pump_event()

def scale_color(rgb, brightness):
    return tuple(int(c * brightness) for c in rgb)

def get_color(percent):
    if percent <= LOW_THRESHOLD:
        return scale_color((255, 0, 0), LED_BRIGHTNESS)         # Red
    elif percent <= MEDIUM_THRESHOLD:
        return scale_color((255, 180, 0), LED_BRIGHTNESS)       # Yellow
    else:
        return scale_color((0, 255, 0), LED_BRIGHTNESS)         # Green

def show_leds(percent):
    leds_on = round(percent / 100 * len(np))
    color = get_color(percent)
    for i in range(len(np)):
        np[i] = color if i < leds_on else (0, 0, 0)
    np.write()

# === Main Loop ===
try:
    while True:
        percent, voltage = read_moisture()
        print("Moisture:", percent, "% (", voltage, "V)")
        post_moisture(percent, voltage)
        show_leds(percent)

        if percent < THRESHOLD:
            run_pump()
            time.sleep(5)  # short cooldown
        else:
            time.sleep(INTERVAL if MODE == "test" else 3600)

except KeyboardInterrupt:
    pump.value(0)
    for i in range(len(np)):
        np[i] = (0, 0, 0)
    np.write()
    print("Stopped by user.")

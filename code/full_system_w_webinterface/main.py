import network, ujson, utime, machine, urequests, socket, gc
from neopixel import NeoPixel
from machine import Pin, ADC, Timer
import ntptime

# === setup pins ===
MOISTURE_PIN = ADC(26)  # A0
PUMP_PIN = Pin(15, Pin.OUT)
LED_PIN = Pin(1, Pin.OUT)
NUM_LEDS = 10
np = NeoPixel(LED_PIN, NUM_LEDS)

# === Globale Variablen ===
history = []
last_pump_time = None
pump_history = []
config = {}

# === load config ===
def load_config():
    global config, mode
    try:
        with open("config.json", "r") as f:
            config = ujson.load(f)
    except:
        import config as fallback
        config = fallback.default_config
    mode = config.get("mode", "interval")

# === WiFi connection ===
def connect_wifi():
    import secrets
    print("connecting to WiFi")
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(secrets.WIFI_SSID, secrets.WIFI_PASSWORD)
    while not wlan.isconnected():
        utime.sleep(0.5)
    print("WiFi connected:", wlan.ifconfig())
    ntptime.settime()

# === Measurements ===
def read_moisture():
    raw = MOISTURE_PIN.read_u16() * 3.3 / 65535
    min_v = config["min_voltage"]
    max_v = config["max_voltage"]
    percent = max(0, min(100, 100 * (max_v - raw) / (max_v - min_v)))
    return round(percent, 1), round(raw, 2)

# === updated LEDs ===
def update_leds(percent):
    num_on = round(NUM_LEDS * percent / 100)
    for i in range(NUM_LEDS):
        if i < num_on:
            if percent < config["low_threshold"]:
                np[i] = (255, 0, 0)
            elif percent < config["medium_threshold"]:
                np[i] = (255, 150, 0)
            else:
                np[i] = (0, 255, 0)
        else:
            np[i] = (0, 0, 0)
    np.write()

# === send data via API ===
def send_data(percent, voltage):
    try:
        import secrets
        headers = {"x-api-key": secrets.API_KEY}
        data = {
            "name": config["name"],
            "sensors": {
                "moisture": {
                    "value": percent,
                    "unit": "%"
                    },
                "moisture-voltage": {
                    "value": voltage,
                    "unit": "V"
                    }
                }
            }
        r = urequests.post(secrets.API_URL + "/measurements", headers=headers, json=data)
        print("Status code:", r.status_code)
        r.close()
    except Exception as e:
        print("API error:", e)

def notify_pump():
    try:
        import secrets
        headers = {"x-api-key": secrets.API_KEY}
        data = {"name": config["name"]}
        r = urequests.post(secrets.API_URL + "/pump", headers=headers, json=data)
        print("Status code:", r.status_code)
        r.close()
    except Exception as e:
        print("Pump notify error:", e)

# === pump control ===
def activate_pump():
    global last_pump_time
    last_pump_time = utime.time()
    pump_history.append(last_pump_time)
    if len(pump_history) > 10:
        pump_history.pop(0)
    duration = config["pump_duration"]
    print("activating pump")
    PUMP_PIN.on()
    utime.sleep(duration)
    PUMP_PIN.off()
    last_pump_time = utime.time()
    notify_pump()
    

# === watering decision ===
def check_watering(percent):
    if percent < config["moisture_threshold"]:
        # z. B. max. 1x pro Stunde gießen
        now = utime.time()
        if not last_pump_time or (now - last_pump_time) > 3600:
            activate_pump()

# === start measurement ===
def measure_and_act():
    global history
    percent, voltage = read_moisture()
    print("Feuchtigkeit:", percent, "% (", voltage, "V)")
    update_leds(percent)
    send_data(percent, voltage)
    history.append((percent, voltage, utime.time()))
    if len(history) > 10:
        history.pop(0)
    check_watering(percent)

# === check time (scheduler mode) ===
def should_run_now():
    now = utime.localtime(utime.time()+ int(2 * 3600)) # UTC offset * seconds
    hhmm = "{:02}:{:02}".format(now[3], now[4])
    print(hhmm)
    return hhmm in config["daily_times"]

# === webinterface ===
def start_webserver():
    import json
    addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
    s = socket.socket()
    s.bind(addr)
    s.listen(1)
    print("Web interface active…")

    while True:
        try:
            cl, _ = s.accept()
            req = cl.recv(1024).decode()
            print("Request:", req.split("\r\n")[0])

            if "GET /data" in req:
                response = {
                    "history": history,
                    "last_pump": last_pump_time,
                    "pump_history": pump_history,
                    "mode": mode
                }
                body = json.dumps(response)
                cl.send("HTTP/1.0 200 OK\r\nContent-Type: application/json\r\n\r\n" + body)

            elif "POST /update" in req:
                length = 0
                for line in req.split("\r\n"):
                    if line.startswith("Content-Length:"):
                        length = int(line.split(":")[1].strip())
                        break
                body = cl.recv(length).decode()
                updates = json.loads(body)
                config.update(updates)
                with open("config.json", "w") as f:
                    json.dump(config, f)
                cl.send("HTTP/1.0 200 OK\r\n\r\nOK")

            elif "POST /pump" in req:
                activate_pump()
                cl.send("HTTP/1.0 200 OK\r\n\r\nPump started")

            elif "GET /" in req or "GET /index.html" in req:
                cl.send("HTTP/1.0 200 OK\r\nContent-Type: text/html\r\n\r\n")
                try:
                    with open("index.html", "r") as f:
                        for line in f:
                            cl.send(line)
                except Exception as e:
                    print("HTML file error:", e)
                    cl.send("Error loading page.")

            else:
                cl.send("HTTP/1.0 404 Not Found\r\n\r\nNot found")

        except Exception as e:
            print("Unhandled error in webserver thread:", e)

        finally:
            try:
                cl.close()
            except:
                pass
            gc.collect()


# === main loop ===
load_config()
connect_wifi()

# run webinterface in the background
import _thread
_thread.start_new_thread(start_webserver, ())

# scheduler for measurements
last_measure = 0

while True:
    now = utime.time()

    if mode == "test":
        if now - last_measure >= 10:
            measure_and_act()
            last_measure = now

    elif mode == "interval":
        interval_seconds = int(config.get("interval_hours", 1) * 3600)
        if now - last_measure >= interval_seconds:
            measure_and_act()
            last_measure = now

    elif mode == "daily":
        # Only run if we're within a minute of a desired time
        if should_run_now():
            if now - last_measure >= 60:
                measure_and_act()
                last_measure = now

    utime.sleep(5)  # small delay to avoid burning CPU


import network
import time
import machine

def connect(ssid, password):
    led = machine.Pin("LED", machine.Pin.OUT)
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('Connecting to network...')
        wlan.connect(ssid, password)
        blink_led(led, times=10, delay=0.1)  # Kurzes Blinken während Verbindung
        while not wlan.isconnected():
            time.sleep(0.5)
    print('Network config:', wlan.ifconfig())
    blink_led(led, times=3, delay=0.3)  # Blinkt 3x, wenn verbunden
    led.on()  # Danach LED dauerhaft an als "connected"
    return wlan.ifconfig()[0]

def blink_led(led, times=5, delay=0.2):
    for _ in range(times):
        led.on()
        time.sleep(delay)
        led.off()
        time.sleep(delay)

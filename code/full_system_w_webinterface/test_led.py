import machine
import neopixel
import time

# Configuration
ADC_PIN = 26           # GP26 = ADC0
NEOPIXEL_PIN = 1       # GP1
NUM_LEDS = 10
MAX_VOLTAGE = 2.5      # Dry
MIN_VOLTAGE = 0.7      # Wet
BRIGHTNESS = 0.2       # Scale 0–1

# Setup
adc = machine.ADC(ADC_PIN)
np = neopixel.NeoPixel(machine.Pin(NEOPIXEL_PIN), NUM_LEDS)

def read_voltage():
    raw = adc.read_u16()  # Range: 0–65535
    voltage = (raw / 65535) * 3.3  # Assuming 3.3 V reference
    return voltage

def map_voltage_to_percent(voltage):
    # Clamp the voltage to expected range
    voltage = max(min(voltage, MAX_VOLTAGE), MIN_VOLTAGE)
    # Invert and map to percentage
    percent = (MAX_VOLTAGE - voltage) / (MAX_VOLTAGE - MIN_VOLTAGE) * 100
    return round(percent, 1)

def get_color(percent):
    if percent <= 30:
        return (255, 0, 0)           # Red
    elif percent <= 50:
        return (255, 180, 0)         # Yellow-orange
    else:
        return (0, 255, 0)           # Green

def show_leds(percent):
    leds_on = round(percent / 100 * NUM_LEDS)
    color = get_color(percent)

    for i in range(NUM_LEDS):
        if i < leds_on:
            np[i] = color
        else:
            np[i] = (0, 0, 0)
    np.write()


try:
    while True:
        voltage = read_voltage()
        percent = map_voltage_to_percent(voltage)
        print("Moisture: {:.1f}% (Voltage: {:.2f} V)".format(percent, voltage))
        show_leds(percent)
        time.sleep(1)
except KeyboardInterrupt:
    for i in range(NUM_LEDS):
        np[i] = (0, 0, 0)
    np.write()
    print("Stopped.")

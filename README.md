# Irrigation Workshop

## Introduction
In this workshop, we will build an automated plant watering system. It will consist of three key components:
1. Sensor – measures soil moisture
2. Pump – delivers water to the plant
3. Controller – reads sensor data and controls the pump

Together, these parts create a responsive system that waters a plant only when it needs it.

### Soil Moisture Sensors

#### Overview

| Sensor Type      | Measurement Principle                    | Advantages                  | Limitations                                    |
|------------------|------------------------------------------|-----------------------------|------------------------------------------------|
| Capacitive       | Measures dielectric constant of the soil | Durable, accurate           | Sensitive to nearby objects and interference   |
| Resistive        | Measures electrical resistance           | Cheap, easy to use          | Corrodes over time (potentially toxic)         |

In addition to resistive and capacitive sensors, there are more advanced methods used in agriculture and research, such as tensiometers, Time Domain Reflectometry or Frequency Domain Reflectometry TDR/FDR sensors, and thermal or capillary-based systems. These offer higher accuracy or different measurement principles (like soil water tension) but are often more complex or expensive.

#### DIY Sensors

Tension Sensors (e.g. Tensiometer, Capillary Sensor)
- Measure how tightly water is held in the soil.
- Simulate what plants "feel" when extracting water.
- Use porous ceramic tips and water-filled tubes to show suction or pressure changes.
- analog output but requires pressure sensor to read electronically -> fun but complex to integrate.

Resistive Sensors (e.g. Nail Electrodes, Gypsum Block)
- Measure electrical resistance between two conductors.
- Moist soil conducts better, dry soil worse (but soil type/quality has an impact too!).
- Simple to build with nails, wires, or embedded in gypsum for more stability.
- analog output (voltage) which is very easy to read with microcontrollers -> simple and easy to integrate.

Tensiometers provide more biologically meaningful data, but are harder to read electronically. Resistive sensors are easier to connect and automate, making them ideal for basic watering systems.

#### Workshop Sensor Choice
For this workshop I recommend using the an off-the-shelf capacitive sensor. They are are more stable and durable than resistive ones. They don’t corrode as quickly, provide smoother readings, and are widely available as well as affordable. This makes them ideal for beginner projects and long-term use in automated watering systems. There are standard sensors that are sold by various shops (see image below). However, they are often faulty. Check this video before you buy some: [Capacitive Soil Moisture Sensors don't work correctly + Fix for v2.0 v1.2 Arduino ESP32 Raspberry Pi](https://www.youtube.com/watch?app=desktop&v=IGP38bz-K48)

![image](img/moisture_sensor.png)

### Pump Systems

| Pump Type         | Working Principle                             | Advantages                        | Suitable For                     |
|-------------------|-----------------------------------------------|-----------------------------------|----------------------------------|
| Submersible Pump  | Impeller submerged in water reservoir         | High flow rate, robust            | Raised beds, greenhouses         |
| Diaphragm Pump    | Oscillating membrane creates pressure/vacuum  | Stable pressure, self-priming     | Distributed watering systems     |
| Peristaltic Pump  | Fluid pushed through flexible tube by rollers | Precise dosage, no backflow       | Potted plants, indoor setups     |

For this workshop, we will use a diaphragm pump. They are reliable, self-priming, and can handle small amounts of water with consistent pressure. They work well in compact systems and are easy to control with a relay or MOSFET. Their sealed design also makes them less prone to leaking or clogging — perfect for small-scale automated irrigation projects.

### Controlling the Pump

Microcontrollers like ESP32 or Arduinos cannot power pumps directly. You need an electronic switch that can handle higher current. There are two common ways to do this: Using a relay or a MOSFET.

| Feature                  | Relay Module                            | MOSFET Module                               |
|--------------------------|-----------------------------------------|---------------------------------------------|
| Switching type           | Mechanical (electromagnetic switch)     | Electronic (transistor-based)               |
| Sound                    | Audible “click” when switching          | Silent                                      |
| Speed                    | Slow switching (ms range)               | Fast switching (μs range), suitable for PWM |
| Load types               | Good for AC and DC                      | Typically used for DC only                  |
| Efficiency               | Some power loss (mechanical contact)    | High efficiency, low heat generation        |
| Use case example         | Simple on/off pump control              | Precise or PWM pump control (e.g. speed)    |
| Complexity               | Easy to wire and understand             | Requires correct polarity and pin setup     |


For this workshop, we will use a MOSFET (IRLB8721PbF). This logic-level MOSFET can be triggered directly from a microcontroller (e.g. Arduino or micro:bit) and is capable of switching up to 24 V DC and 10 A — more than enough for most small pumps or valves. It's silent, efficient, and ideal for low-voltage DC systems.
While the pumps used in this setup typically draw far less current (around 500 mA), using a higher-rated MOSFET gives us more flexibility. It ensures that the same circuit can also be used safely with larger pumps or other components in future projects.

(Wiring example check [here](https://learn.adafruit.com/rgb-led-strips/usage)) 

NOTE: Pico AND MOSFET/Pump Power Source MUST HAVE THE SAME GROUND!!


## Setup and Code

### Wiring the components

![image](img/fritzing_circuit_bb.png)

### Switch GPIO output on and off

```python
import machine
import time

# Set the pump control pin
PUMP_PIN = 15  # Use GPIO15, change if needed
pump = machine.Pin(PUMP_PIN, machine.Pin.OUT)

def pump_on():
    pump.value(1)  # Set pin HIGH to turn pump ON
    print("Pump ON")

def pump_off():
    pump.value(0)  # Set pin LOW to turn pump OFF
    print("Pump OFF")

# Simple test sequence
while True:
    print("Turning pump ON for 3 seconds...")
    pump_on()
    time.sleep(3)
        
    print("Turning pump OFF for 3 seconds...")
    pump_off()
    time.sleep(3)

```

### Reading Sensor Data

```python
from machine import Pin, ADC
from time import sleep

soil = ADC(Pin(26))

while True:
  soil_value = soil.read_u16() # read value, 0-65535 across voltage range 0.0v - 3.3v
  soil_voltage = (soil_value/65535)*3.3
  print(soil_voltage) 
  sleep(1)

```

### Test LED strips

```python

import machine
import neopixel
import time

# Configuration
NUM_LEDS = 10
PIN = 1
BRIGHTNESS = 100  # 0–255

np = neopixel.NeoPixel(machine.Pin(PIN), NUM_LEDS)

# Helper: apply brightness to RGB
def scale_color(r, g, b, brightness):
    factor = brightness / 255
    return int(r * factor), int(g * factor), int(b * factor)

# Helper: turn off all LEDs
def clear_strip():
    for i in range(NUM_LEDS):
        np[i] = (0, 0, 0)
    np.write()

# List of colors to cycle through
colors = [
    (255, 0, 0),   # Red
    (0, 255, 0),   # Green
    (0, 0, 255)    # Blue
]

# Main running light loop
try:
    color_index = 0
    while True:
        r, g, b = colors[color_index]
        r, g, b = scale_color(r, g, b, BRIGHTNESS)

        # Forward direction
        for i in range(NUM_LEDS):
            clear_strip()
            np[i] = (r, g, b)
            np.write()
            time.sleep(0.1)

        # Backward direction
        for i in range(NUM_LEDS - 2, 0, -1):
            clear_strip()
            np[i] = (r, g, b)
            np.write()
            time.sleep(0.1)

        # Next color
        color_index = (color_index + 1) % len(colors)

except KeyboardInterrupt:
    clear_strip()
    print("Running light stopped.")


```

## Interfaces


## Similar Projects

### Self-Watering Flower Pot "Flaura"
This 3D-printable self-watering flower pot project integrates a soil moisture sensor, a microcontroller (ESP8266), and a small water pump to automate plant care. It also includes a mobile app interface using Blynk, allowing users to monitor soil moisture and trigger manual watering remotely.

https://www.thingiverse.com/thing:4921885


### Watering System without microcontroller
This project builds a simple automatic plant watering system without using a microcontroller. It uses soil probes to detect moisture, a BC547 transistor to trigger a relay, and a small water pump. When the soil is dry, the pump automatically turns on; when the soil is wet, it turns off. It's a low-cost solution with no programming required.

https://circuitdigest.com/electronic-circuits/automatic-plant-watering-system-without-arduino

### xx

https://www.elecrow.com/smart-plant.html

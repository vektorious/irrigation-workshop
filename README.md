# Irrigation Workshop

## Introduction
In this workshop, we will build an automated plant watering system. It will consist of three key components:
1. Sensor – measures soil moisture
2. Pump – delivers water to the plant
3. Controller – reads sensor data and controls the pump

Together, these parts create a responsive system that waters a plant only when it needs it.

## Soil Moisture Sensors

### Overview

| Sensor Type      | Measurement Principle                    | Advantages                  | Limitations                                    |
|------------------|------------------------------------------|-----------------------------|------------------------------------------------|
| Capacitive       | Measures dielectric constant of the soil | Durable, accurate           | Sensitive to nearby objects and interference   |
| Resistive        | Measures electrical resistance           | Cheap, easy to use          | Corrodes over time (potentially toxic)         |

In addition to resistive and capacitive sensors, there are more advanced methods used in agriculture and research, such as tensiometers, Time Domain Reflectometry or Frequency Domain Reflectometry TDR/FDR sensors, and thermal or capillary-based systems. These offer higher accuracy or different measurement principles (like soil water tension) but are often more complex or expensive.

### DIY Sensors

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

### Resources

https://www.youtube.com/watch?app=desktop&v=IGP38bz-K48


## Pump Systems

| Pump Type         | Working Principle                             | Advantages                        | Suitable For                     |
|-------------------|-----------------------------------------------|-----------------------------------|----------------------------------|
| Submersible Pump  | Impeller submerged in water reservoir         | High flow rate, robust            | Raised beds, greenhouses         |
| Diaphragm Pump    | Oscillating membrane creates pressure/vacuum  | Stable pressure, self-priming     | Distributed watering systems     |
| Peristaltic Pump  | Fluid pushed through flexible tube by rollers | Precise dosage, no backflow       | Potted plants, indoor setups     |


## Controlling the Pump

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

For this workshop, we have these available:
- Regular microcontroller-ready relay modules
- MOSFET (IRLB8721PbF) suitable for switching upt to 24V DC and 10A (Wiring example check [here](https://learn.adafruit.com/rgb-led-strips/usage))

**Example script switching a GPIO output on and off**

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


## Reading Sensor Data

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


## Interfaces


## Similar Projects

### Self-Watering Flower Pot "Flaura"
This 3D-printable self-watering flower pot project integrates a soil moisture sensor, a microcontroller (ESP8266), and a small water pump to automate plant care. It also includes a mobile app interface using Blynk, allowing users to monitor soil moisture and trigger manual watering remotely.

https://www.thingiverse.com/thing:4921885


### Watering System without microcontroller
This project builds a simple automatic plant watering system without using a microcontroller. It uses soil probes to detect moisture, a BC547 transistor to trigger a relay, and a small water pump. When the soil is dry, the pump automatically turns on; when the soil is wet, it turns off. It's a low-cost solution with no programming required.

https://circuitdigest.com/electronic-circuits/automatic-plant-watering-system-without-arduino

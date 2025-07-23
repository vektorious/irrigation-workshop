from machine import Pin, ADC
from time import sleep

soil = ADC(Pin(26))

while True:
  soil_value = soil.read_u16() # read value, 0-65535 across voltage range 0.0v - 3.3v
  soil_voltage = (soil_value/65535)*3.3
  print(soil_voltage) 
  sleep(1)

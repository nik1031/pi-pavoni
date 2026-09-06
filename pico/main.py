from machine import ADC
from utime import sleep

#Initialise pressure readings on Pin 26
pressure_pin = ADC(26)


while True:

  # read_u16() returns a 16-bit integer from 0 to 65535
  raw_value = pressure_pin.read_u16()

  # Convert raw reading to actual voltage (0.0 to 3.3V)
  voltage = raw_value * (3.3 / 65535)
  pressure_bars = raw_value * (16/65535)

  print(f"Raw: {raw_value} | Voltage: {voltage:.2f} | Pressure: {pressure_bars:.2f}bars")
  sleep(1)
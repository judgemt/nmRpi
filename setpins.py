import RPi.GPIO as GPIO
import json
import time
from drivers.utils import calibrate_sleep_overhead, step, Microstep

config_file = 'config/pin_map.json'
"""Initialize stepper with GPIO pin mappings and microstep pins."""
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

with open(config_file, 'r') as file:
    pins = json.load(file)

#####################################################

"""Set up the GPIO pins."""
try:
    # Set all pins to defaults first
    for pin_name, pin in pins.items():
        print(f"Setting up {pin_name} pin at GPIO {pin['number']}")
        GPIO.setup(pin['number'], GPIO.OUT)

        initial_state = GPIO.LOW if pin['init'] == "LOW" else GPIO.HIGH
        GPIO.output(pin['number'], initial_state)  # Set all pins to initial state
    
    # Now, set up microstepping independent of the other pins
    microstep = Microstep(pins)

    pins_setup = True
    print("All pins set up successfully.")

except Exception as e:
    print(f"Error during pin setup: {e}")
    pins_setup = False

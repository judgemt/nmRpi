from drivers.stepper import A4988
from drivers.pump_v0 import Pump
import RPi.GPIO as GPIO
import time

# Define pin mappings for motor control - don't forget to check config/pin_map.json

# Initialize stepper with auto-calibration
stepper = A4988(config_file='config/pin_map.json', auto_calibrate=True, speed=2, pulseWidth=5E-6)

# Initialize pump object globally (could make this session-specific later)
 
pump = Pump(motor=stepper, syringe_volume=4, ml_per_rotation=4.5/5, step_mode='sixteenth')

pump.print_info()

pump.move_volume(21, speed=.5)

pump.print_info()
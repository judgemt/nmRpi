from drivers.stepper import A4988
from drivers.pump_v0 import Pump
import RPi.GPIO as GPIO
import time

# Define pin mappings for motor control - don't forget to check config/pin_map.json

# Initialize stepper with auto-calibration
stepper = A4988(config_file='config/pin_map.json', 
                enable_pin=37, 
                auto_calibrate=False,  # Changed to False initially
                speed=2, 
                pulseWidth=5E-6)

# Set up pins and calibrate explicitly
stepper.setup_pins()
stepper.calibrate()

# Initialize pump object globally
pump = Pump(motor=stepper, syringe_volume=4, ml_per_rotation=4.5/5, step_mode='sixteenth')

# Enable the pump before use
pump.enable()

pump.print_info()

pump.move_volume(21, speed=.5)

pump.print_info()

# Clean up
pump.disable()
stepper.cleanup()
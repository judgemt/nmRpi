from drivers.stepper import A4988
from drivers.pump_v0 import Pump
import RPi.GPIO as GPIO
import time

# Define pin mappings for motor control

pin_map = {
    'DIR': {'number': 27, 'init': GPIO.LOW},
    'STEP': {'number': 26, 'init': GPIO.LOW},
    'MS3': {'number': 23, 'init': GPIO.LOW},
    'MS2': {'number': 22, 'init': GPIO.LOW},
    'MS1': {'number': 21, 'init': GPIO.LOW},
    'ENABLE': {'number': 20, 'init': GPIO.HIGH},
}

# Initialize stepper with auto-calibration
stepper = A4988(pin_mappings=pin_map, auto_calibrate=True, speed=2, pulseWidth=5E-6)

# Initialize pump object globally (could make this session-specific later)
 
pump = Pump(motor=stepper, syringe_volume=5, ml_per_rotation=1, step_mode='sixteenth')

pump.print_info()

pump.move_volume(2, speed=1)

pump.print_info()
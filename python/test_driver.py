from drivers.stepper import A4988
import RPi.GPIO as GPIO

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

# Move without pre-setting the step mode
stepper.move(revolutions=3, stepMode="full", direction="CW", speed=2)
stepper.move(revolutions=3, stepMode="half", direction="CW", speed=2)
stepper.move(revolutions=3, stepMode="quarter", direction="CW", speed=2)
stepper.move(revolutions=3, stepMode="eighth", direction="CW", speed=2)
stepper.move(revolutions=3, stepMode="sixteenth", direction="CW", speed=2)

# Cleanup GPIO
# stepper.cleanup()

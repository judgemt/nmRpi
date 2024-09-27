import RPi.GPIO as GPIO
import time

from a4988_sim.pin_reader import PinReader
from a4988_sim.a4988_stepper import A4988Stepper

# Main script

GPIO.setmode(GPIO.BCM)

try:
    # Define pin layout
    pin_map = {
        'MS1': 4,
        'MS2': 5,
        'MS3': 6,
        'STEP': 21,
        'DIR': 20,
        'ENABLE': 22
    }

    input_pin = {
        'STEP': 23,
        'ENABLED': 19,
        'MS1': 13,
        'MS2': 16,
        'MS3': 17,
        'DIR': 24
    }

    # Create instances of the classes
    driver_state = PinReader(input_pin)
    stepper = A4988Stepper(pin_mappings=pin_map, microstep_settings=(0, 0, 0), pin_reader=driver_state)

    buttonPin = 27
    GPIO.setup(buttonPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    # Main logic loop
    steps = 0
    stepper.set_direction("CW")  # Set initial direction to Clockwise
    stepper.enable()  # Enable the motor driver

    while True:
        if GPIO.input(buttonPin) == GPIO.LOW:  # Button pressed (PUD_UP makes LOW = pressed)
            print('Button pressed, stepping motor')
            stepper.step()  # Perform one motor step
            steps += 1
            print(f"Total steps: {steps}")
            driver_state.update()  # Update pin readings
            driver_state.print_states(stepper.pins)  # Print updated pin states
            time.sleep(0.25)  # Debounce the button

        time.sleep(0.1)  # Short sleep to reduce CPU usage

except KeyboardInterrupt:
    print("Interrupted by user, exiting...")

finally:
    # Cleanup GPIO
    GPIO.cleanup()
    print("GPIO cleanup complete")

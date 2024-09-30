import RPi.GPIO as GPIO
import time

from a4988_sim.a4988_stepper import A4988Stepper

# Main script

GPIO.setmode(GPIO.BCM)

try:
    # Define pin layout
    pin_map = {
        'DIR': 17,
        'STEP': 16,
        'MS3': 13,
        'MS2': 12,
        'MS1': 6,
        'ENABLE': 5
    }

    # Create instances of the classes
    stepper = A4988Stepper(pin_mappings=pin_map, microstep_settings=(0, 0, 0))

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
            time.sleep(0.25)  # Debounce the button

        time.sleep(0.1)  # Short sleep to reduce CPU usage

except KeyboardInterrupt:
    print("Interrupted by user, exiting...")

finally:
    # Cleanup GPIO
    GPIO.cleanup()
    print("GPIO cleanup complete")

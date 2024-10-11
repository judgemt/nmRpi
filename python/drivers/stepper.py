import RPi.GPIO as GPIO
import time
from drivers.utils import calibrate_step_delay, step
from drivers.utils import Microstep

class A4988:
    def __init__(self, pin_mappings, auto_calibrate=False, speed=None, pulseWidth=None, motor_spr=200):
        """Initialize stepper with GPIO pin mappings and microstep pins."""
        GPIO.setmode(GPIO.BCM)
        self.pins = pin_mappings
        self.stepDelay = None  # Field to store the calibrated step delay
        self.pins_setup = False  # Flag to check if pins are set up correctly
        self.microstep = None  # this will handle microstepping
        self.motor_spr = motor_spr  # steps per revolution; default for nema17 pololu is 200
        
        # Set up GPIO and verify pin setup
        self.setup_pins()

        # Optional auto-calibration during initialization
        if auto_calibrate:
            if speed is None or pulseWidth is None:
                raise ValueError("Speed and pulseWidth must be provided for auto calibration.")
            self.calibrate(speed, pulseWidth)

    def setup_pins(self):
        """Set up the GPIO pins."""
        try:
            # Set all pins to defaults first
            for pin_name, pin in self.pins.items():
                print(f"Setting up {pin_name} pin at GPIO {pin['number']}")
                GPIO.setup(pin['number'], GPIO.OUT)
                GPIO.output(pin['number'], pin['init'])  # Set all pins to initial state
            
            # Now, set up microstepping independent of the other pins
            self.microstep = Microstep(self.pins)

            self.pins_setup = True
            print("All pins set up successfully.")

        except Exception as e:
            print(f"Error during pin setup: {e}")
            self.pins_setup = False

    def enable(self):
        """Enable the motor driver (ENABLE pin is active low)."""
        if not self.pins_setup:
            raise RuntimeError("Pins have not been set up correctly.")
        GPIO.output(self.pins['ENABLE']['number'], GPIO.LOW)
        print(f"Motor enabled")

    def disable(self):
        """Disable the motor driver (ENABLE pin is active low)."""
        if not self.pins_setup:
            raise RuntimeError("Pins have not been set up correctly.")
        GPIO.output(self.pins['ENABLE']['number'], GPIO.HIGH)
        print(f"Motor disabled")

    def set_direction(self, direction):
        """Set direction to Clockwise (HIGH) or Counter-Clockwise (LOW)."""
        if not self.pins_setup:
            raise RuntimeError("Pins have not been set up correctly.")
        if direction == "CW":
            GPIO.output(self.pins['DIR']['number'], GPIO.HIGH)
            print(f"Direction set to Clockwise")
        else:
            GPIO.output(self.pins['DIR']['number'], GPIO.LOW)
            print(f"Direction set to Counter-Clockwise")

    def calibrate(self, speed, pulseWidth):
        """Calibrate the step delay based on speed and pulseWidth and store it."""
        if not self.pins_setup:
            raise RuntimeError("Pins have not been set up correctly.")
        if self.microstep is None:
            raise RuntimeError("Microstep object not initialized.")
        spr = self.microstep.get_factor() * self.motor_spr  # Use self.motor_spr instead of hardcoding 200
        self.stepDelay = calibrate_step_delay(spr, speed, pulseWidth, 1E4)
        print(f"Calibration complete: stepDelay = {self.stepDelay}")

    def set_step_type(self, stepMode):
        """Set the step mode (full, half, quarter, sixteenth) without moving the motor."""
        print(f"Setting step mode to {stepMode}")
        self.microstep.set_mode(stepMode)
        print(f"Step mode {stepMode} set successfully.")

    def move(self, revolutions, stepMode, direction="CW", pulseWidth=5E-6):
        """Move the stepper motor by a given number of revolutions in the specified direction."""
        if not self.pins_setup:
            raise RuntimeError("Pins have not been set up correctly.")
        
        # Automatically calibrate if not done yet
        if self.stepDelay is None:
            print("Calibration not done. Running automatic calibration...")
            raise RuntimeError("Step delay not calibrated. Please run calibrate() first.")

        # Set step mode using the set_step_type function
        self.set_step_type(stepMode)

        spr = self.microstep.get_factor() * self.motor_spr
        steps = spr * revolutions

        # Enable the motor
        self.enable()

        # Set direction based on input
        self.set_direction(direction)

        # Perform the steps
        print(f"Moving {revolutions} revolutions in {stepMode} mode in {direction} direction.")
        time_elapsed = step(steps, self.pins, pulseWidth, self.stepDelay)
        print(f"Speed measured @ {round(revolutions / time_elapsed, 3)} rps")

        # Disable the motor after movement is complete
        self.disable()

    def cleanup(self):
        """Clean up the GPIO resources."""
        print("Cleaning up GPIO resources for the stepper.")
        GPIO.cleanup()


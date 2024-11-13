import RPi.GPIO as GPIO
import time
from drivers.utils import calibrate_sleep_overhead, step, Microstep
import json

class A4988:
    def __init__(self, config_file, auto_calibrate=False, speed=None, pulseWidth=None, motor_spr=200):
        """Initialize stepper with GPIO pin mappings and microstep pins."""
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        with open(config_file, 'r') as file:
            self.pins = json.load(file)

        self.stepDelay = None  # This will be dynamically calculated
        self.sleep_overhead = None  # To store the calibrated sleep overhead
        self.pins_setup = False  # Flag to check if pins are set up correctly
        self.microstep = None  # this will handle microstepping
        self.motor_spr = motor_spr  # steps per revolution; default for nema17 pololu is 200
        self.pulseWidth = pulseWidth or 5E-6  # Default pulse width
        self.enabled = False  # Add field to track the motor's enabled state

        # Set up GPIO and verify pin setup
        GPIO.setwarnings(False)
        self.setup_pins()

        # Optional auto-calibration during initialization
        if auto_calibrate:
            if speed is None or pulseWidth is None:
                raise ValueError("Speed and pulseWidth must be provided for auto calibration.")
            self.calibrate()
    
    def set_pin_state(self, pin_name, state):
        """Set the state of a GPIO pin."""
        if pin_name not in self.pins:
            raise ValueError(f"Pin {pin_name} is not defined in the configuration.")
        GPIO.output(self.pins[pin_name]['number'], state)

    def setup_pins(self):
        """Set up the GPIO pins."""
        try:
            for pin_name, pin in self.pins.items():
                print(f"Setting up {pin_name} pin at GPIO {pin['number']}")
                GPIO.setup(pin['number'], GPIO.OUT)
                initial_state = GPIO.LOW if pin['init'] == "LOW" else GPIO.HIGH
                self.set_pin_state(pin_name, initial_state)

                if pin_name == "ENABLE":
                    self.enabled = (initial_state == GPIO.LOW)

            self.microstep = Microstep(self.pins)
            self.pins_setup = True
            print("All pins set up successfully.")

        except Exception as e:
            print(f"Error during pin setup: {e}")
            self.pins_setup = False
            self.enabled = False

    def enable(self):
        """Enable the motor driver (ENABLE pin is active low)."""
        if not self.pins_setup:
            raise RuntimeError("Pins have not been set up correctly.")
        GPIO.output(self.pins['ENABLE']['number'], GPIO.LOW)
        self.enabled = True  # Update the enabled state
        print("Motor enabled")

    def disable(self):
        """Disable the motor driver (ENABLE pin is active low)."""
        if not self.pins_setup:
            raise RuntimeError("Pins have not been set up correctly.")
        GPIO.output(self.pins['ENABLE']['number'], GPIO.HIGH)
        self.enabled = False  # Update the enabled state
        print("Motor disabled")

    def set_direction(self, direction):
        """Set direction to Clockwise (HIGH) or Counter-Clockwise (LOW)."""
        if not self.pins_setup:
            raise RuntimeError("Pins have not been set up correctly.")
        if not self.enabled:
            raise RuntimeError("Motor is not enabled. Please enable the motor before setting direction.")
        if direction == "CW":
            GPIO.output(self.pins['DIR']['number'], GPIO.HIGH)
            print(f"Direction set to Clockwise")
        else:
            GPIO.output(self.pins['DIR']['number'], GPIO.LOW)
            print(f"Direction set to Counter-Clockwise")

    def calibrate(self):
        """Calibrate the sleep overhead and store it."""
        if not self.pins_setup:
            raise RuntimeError("Pins have not been set up correctly.")
        if not self.enabled:
            raise RuntimeError("Motor is not enabled. Please enable the motor before calibration.")
        
        # Measure and store the sleep overhead using the new calibration function
        self.sleep_overhead = calibrate_sleep_overhead()  # Only measure sleep overhead
        print(f"Calibration complete: sleep_overhead = {self.sleep_overhead}")

    def set_step_type(self, stepMode):
        """Set the step mode (full, half, quarter, sixteenth) without moving the motor."""
        print(f"Setting step mode to {stepMode}")
        self.microstep.set_mode(stepMode)
        print(f"Step mode {stepMode} set successfully.")

    def move(self, revolutions=None, steps=None, stepMode="full", speed=1, direction="CW", pulseWidth=5E-6):
        """Move the stepper motor by a given number of revolutions or steps in the specified direction."""
        if not self.pins_setup:
            raise RuntimeError("Pins have not been set up correctly.")
        if not self.enabled:
            raise RuntimeError("Motor is not enabled. Please enable the motor before attempting to move.")       
        if self.sleep_overhead is None:
            raise RuntimeError("Sleep overhead not calibrated. Please run calibrate() first.")

        # Set microstepping mode
        self.microstep.set_mode(stepMode)
        spr = self.microstep.get_factor() * self.motor_spr  # Steps per revolution

        # Determine if we're moving by revolutions or steps
        if steps is not None:
            total_steps = steps
            revolutions = total_steps / spr  # Convert steps to revolutions for rps reporting
            print(f"Moving {steps} steps in {stepMode} mode, which is {revolutions:.3f} revolutions.")
        elif revolutions is not None:
            total_steps = spr * revolutions
            print(f"Moving {revolutions} revolutions in {stepMode} mode, which is {total_steps} steps.")
        else:
            raise ValueError("Either revolutions or steps must be provided.")
        total_steps = int(round(total_steps))

        # Calculate steps per second (SPS)
        sps = spr * speed

        # Calculate stepDelay based on speed, sleep overhead, and pulse width
        step_desired = 1 / sps
        self.stepDelay = step_desired - self.sleep_overhead - pulseWidth
        self.stepDelay = max(self.stepDelay, pulseWidth)  # Ensure minimum step delay
        
        # Enable the motor
        self.enable()

        # Set direction based on input
        self.set_direction(direction)

        # Perform the steps
        time_elapsed = step(total_steps, self.pins, pulseWidth, self.stepDelay)
        
        # Calculate revolutions per second (rps)
        measured_rps = revolutions / time_elapsed
        print(f"Movement complete. Speed measured @ {round(measured_rps, 3)} rps.")

        # Disable the motor after movement is complete
        self.disable()

    def cleanup(self):
        """Clean up the GPIO resources."""
        print("Cleaning up GPIO resources for the stepper.")
        GPIO.cleanup()


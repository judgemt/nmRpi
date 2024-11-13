import RPi.GPIO as GPIO
import time
from drivers.utils import calibrate_sleep_overhead, step, Microstep
import json

class A4988:
    
    # Pin label constants
    PIN_ENABLE = "ENABLE"
    PIN_DIRECTION = "DIR"
    PIN_STEP = "STEP"
 
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
    
    def _validate_state(self, require_enabled=False, require_calibrated=False):
        """
        Validates the state of the motor and raises appropriate errors if conditions are not met.
        
        Args:
            require_enabled (bool): If True, checks if the motor is enabled.
            require_calibrated (bool): If True, checks if the sleep overhead is calibrated.
        """
        if not self.pins_setup:
            raise RuntimeError("Pins have not been set up correctly.")
        if require_enabled and not self.enabled:
            raise RuntimeError("Motor is not enabled. Please enable the motor before proceeding.")
        if require_calibrated and self.sleep_overhead is None:
            raise RuntimeError("Sleep overhead not calibrated. Please run calibrate() first.")

    def set_pin_state(self, pin_name, state):
        """
        Set the state of a GPIO pin.

        Args:
            pin_name (str): Name of the pin (e.g., 'ENABLE', 'DIR').
            state (int): Desired GPIO state (GPIO.HIGH or GPIO.LOW).

        Raises:
            ValueError: If the pin name is not defined or not configured as output.
        """
        if pin_name not in self.pins:
            raise ValueError(f"Pin {pin_name} is not defined in the configuration.")
        if not GPIO.gpio_function(self.pins[pin_name]['number']) == GPIO.OUT:
            raise ValueError(f"Pin {pin_name} is not configured as an output pin.")
        
        GPIO.output(self.pins[pin_name]['number'], state)
        print(f"Set pin {pin_name} to {'HIGH' if state == GPIO.HIGH else 'LOW'}.")

    def setup_pins(self):
        """Set up the GPIO pins."""
        try:
            for pin_name, pin in self.pins.items():
                print(f"Setting up {pin_name} pin at GPIO {pin['number']}")
                GPIO.setup(pin['number'], GPIO.OUT)
                initial_state = GPIO.LOW if pin['init'] == "LOW" else GPIO.HIGH
                self.set_pin_state(pin_name, initial_state)

                if pin_name == self.PIN_ENABLE:
                    self.enabled = (initial_state == GPIO.LOW)

            self.microstep = Microstep(self.pins)
            self.pins_setup = True
            print("All pins set up successfully.")

        except Exception as e:
            print(f"Error during pin setup: {e}. You may want to disconnect power to motor to avoid damage.")
            self.pins_setup = False
            self.enabled = False
            # Clean up GPIO resources only in case of failure
            GPIO.cleanup()
            
    def enable(self):
        """Enable the motor driver (ENABLE pin is active low)."""
        self._validate_state()
        GPIO.output(self.pins['ENABLE']['number'], GPIO.LOW)
        self.enabled = True  # Update the enabled state
        print("Motor enabled")

    def disable(self):
        """Disable the motor driver (ENABLE pin is active low)."""
        self._validate_state()
        GPIO.output(self.pins['ENABLE']['number'], GPIO.HIGH)
        self.enabled = False  # Update the enabled state
        print("Motor disabled")

    def set_direction(self, direction):
        """Set direction to Clockwise (HIGH) or Counter-Clockwise (LOW)."""
        self._validate_state(require_enabled=True)

        if direction == "CW":
            GPIO.output(self.pins['DIR']['number'], GPIO.HIGH)
            print(f"Direction set to Clockwise")
        else:
            GPIO.output(self.pins[self.PIN_DIRECTION]['number'], GPIO.LOW)
            print(f"Direction set to Counter-Clockwise")

    def calibrate(self):
        """Calibrate the sleep overhead and store it."""
        self._validate_state(require_enabled=True)

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
        self._validate_state(require_enabled=True, require_calibrated=True)

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

    def reset(self):
        """Reset the motor to a safe state."""
        try:
            print("Resetting motor to safe state...")
            # Disable the motor to ensure it's not active during reset
            if self.enabled:
                self.disable()
            # Reinitialize GPIO pins
            self.setup_pins()
            print("Motor reset successfully.")
        except Exception as e:
            print(f"Error during motor reset: {e}")
            self.pins_setup = False
            self.enabled = False
            
    def cleanup(self):
        """Clean up the GPIO resources."""
        print("Cleaning up GPIO resources for the stepper.")
        GPIO.cleanup()


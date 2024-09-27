import RPi.GPIO as GPIO
import time

class A4988Stepper:
    def __init__(self, pin_mappings, microstep_settings=(0, 0, 0), pin_reader=None):
        self.pins = pin_mappings
        self.pin_reader = pin_reader  # Instance of PinReader to read inputs
        
        # Set up GPIO
        for pin_name, pin in self.pins.items():
            print(f"Setting up {pin_name} pin at GPIO {pin}")
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, GPIO.LOW)  # Set all pins to LOW initially

        # Set the initial microstepping mode
        self.set_microstepping(*microstep_settings)

    def set_microstepping(self, ms1=None, ms2=None, ms3=None):
        """Set microstepping mode by adjusting MS1, MS2, MS3 pins."""
        if ms1 is None and ms2 is None and ms3 is None:
            print("Microstepping Map:")
            print("Full       | Low   | Low   | Low")
            print("Half       | High  | Low   | Low")
            print("Quarter    | Low   | High  | Low")
            print("Eighth     | High  | High  | Low")
            print("Sixteenth  | High  | High  | High")
        else:
            # Set the microstepping pins if arguments are provided
            self.microstepping_settings = (ms1, ms2, ms3)
            GPIO.output(self.pins['MS1'], ms1)
            GPIO.output(self.pins['MS2'], ms2)
            GPIO.output(self.pins['MS3'], ms3)
            print(f"Microstepping set to {self.microstepping_settings}")
            if self.pin_reader:
                self.pin_reader.update()

    def enable(self):
        """Enable the motor driver (ENABLE pin is active low)."""
        GPIO.output(self.pins['ENABLE'], GPIO.LOW)  # LOW to enable
        print(f"Motor enabled with ENABLE pin {self.pins['ENABLE']}")
        if self.pin_reader:
            self.pin_reader.update()

    def disable(self):
        """Disable the motor driver (ENABLE pin is active low)."""
        GPIO.output(self.pins['ENABLE'], GPIO.HIGH)  # HIGH to disable
        print(f"Motor disabled with ENABLE pin {self.pins['ENABLE']}")
        if self.pin_reader:
            self.pin_reader.update()

    def set_direction(self, direction):
        """Set direction to Clockwise (HIGH) or Counter-Clockwise (LOW)."""
        if direction == "CW":
            GPIO.output(self.pins['DIR'], GPIO.HIGH)
            print(f"Setting DIR pin {self.pins['DIR']} to HIGH for CW")
        else:
            GPIO.output(self.pins['DIR'], GPIO.LOW)
            print(f"Setting DIR pin {self.pins['DIR']} to LOW for CCW")
        if self.pin_reader:
            self.pin_reader.update()

    def step(self):
        """Perform a single step (toggle the STEP pin)."""
        GPIO.output(self.pins['STEP'], GPIO.HIGH)
        print("STEP pin set to HIGH")  # Output pin state for readability

        if self.pin_reader:
            self.pin_reader.update()  # Capture the HIGH state before toggling to LOW
            self.pin_reader.print_states(self.pins)  # Optionally print pin states right after the update

        time.sleep(0.001)  # Step pulse width
        GPIO.output(self.pins['STEP'], GPIO.LOW)
        print("STEP pin set to LOW")  # Output pin state for readability

    def cleanup(self):
        """Clean up the GPIO resources when done."""
        print("Cleaning up A4988Stepper GPIO")

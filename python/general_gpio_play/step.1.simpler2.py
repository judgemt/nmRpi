import RPi.GPIO as GPIO
import time

GPIO.cleanup()

# Define Pin Layout
GPIO.setmode(GPIO.BCM)  # Set BCM mode once globally

## Set up simulated A4988 driver:
pin_map = {
    'MS1': 4,   # pull up to activate 
    'MS2': 5,   # pull up to activate
    'MS3': 6,   # pull up to activate
    'STEP': 21, # each HIGH pulse triggers next step according to ms settings
    'DIR': 20,  # pull up for clockwise, pull down for counterclockwise
    'ENABLE': 22 # enable motor driver
}

input_pin = {
    'STEP': 23,
    'ENABLED': 19,
    'MS1': 13,
    'MS2': 16,
    'MS3': 17,
    'DIR': 24
}


class PinReader:
    def __init__(self, pin_mappings):
        """Initialize GPIO pins for reading."""
        self.pins = pin_mappings
        self.pin_states = {}  # Dictionary to store the state of each pin

        # Set up each pin as an input with pull-down resistors
        for pin_name, pin in self.pins.items():
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    
    def update(self):
        """Read and store the current state of all pins."""
        for pin_name, pin_number in self.pins.items():
            self.pin_states[pin_name] = GPIO.input(pin_number)

    def print_states(self, output_pins):
        """Print the stored state of all pins."""
        print("A4988 Pin Readings:")
        for pin_name, pin_state in self.pin_states.items():
            state_str = "HIGH" if pin_state else "LOW"
            output_pin = output_pins.get(pin_name, None)
            if output_pin:
                print(f"{pin_name}: {state_str} (from GPIO {output_pin}, to GPIO {self.pins[pin_name]})")
            else:
                print(f"{pin_name}: {state_str} (GPIO {self.pins[pin_name]})")

    def cleanup(self):
        """Clean up GPIO resources."""
        print("Cleaning up PinReader GPIO")
        GPIO.cleanup()


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
            self.microstep_settings = (ms1, ms2, ms3)
            GPIO.output(self.pins['MS1'], ms1)
            GPIO.output(self.pins['MS2'], ms2)
            GPIO.output(self.pins['MS3'], ms3)
            print(f"Microstepping set to {self.microstep_settings}")
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
        time.sleep(0.001)  # Step pulse width
        GPIO.output(self.pins['STEP'], GPIO.LOW)
        print(f"Stepping with STEP pin {self.pins['STEP']}")
        if self.pin_reader:
            self.pin_reader.update()

    def cleanup(self):
        """Clean up the GPIO resources when done."""
        print("Cleaning up A4988Stepper GPIO")
        GPIO.cleanup()


# Create an instance of the PinReader for input pins
driver_state = PinReader(input_pin)

# Create an instance of the A4988Stepper with the PinReader
stepper = A4988Stepper(pin_mappings=pin_map, microstep_settings=(0, 0, 0), pin_reader=driver_state)

buttonPin = 27
GPIO.setup(buttonPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

## Make static modifications and read out

try:
    # When stepper.pin_reader is updated, it updates the driver_state object
    stepper.set_direction("CW")  # This updates the pin_reader, which is driver_state
    
    # Update and print the driver_state pin readings
    driver_state.update()
    driver_state.print_states(stepper.pins)

    # Additional logic (e.g., handling button presses) goes here

finally:
    # Cleanup GPIO at the end
    stepper.cleanup()
    driver_state.cleanup()

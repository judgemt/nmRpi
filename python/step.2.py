import RPi.GPIO as GPIO
import time

# Define Pin Layout
GPIO.setmode(GPIO.BCM)  # Set BCM mode once globally

## Set up simulated A4988 driver:
pin_map = {
    'MS1': 4,  # pull up to activate 
    'MS2': 5,  # pull up to activate
    'MS3': 6,  # pull up to activate
    'STEP': 21,  # each HIGH pulse triggers next step according to ms settings
    'DIR': 20,   # pull up for clockwise, pull down for counterclockwise
    'ENABLE': 22  # enable motor driver
}

class PinReader:
    def __init__(self, pin_mappings):
        """Initialize GPIO pins for reading."""
        self.pins = pin_mappings
        self.pin_states = {}  # Dictionary to store the state of each pin

        # Set up each pin as an input with pull-down resistors
        for pin in self.pins.values():
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    def update(self):
        """Read and store the current state of all pins."""
        for pin_name, pin_number in self.pins.items():
            self.pin_states[pin_name] = GPIO.input(pin_number)

    def print_states(self):
        """Print the stored state of all pins."""
        print("Pin States:")
        for pin_name, pin_state in self.pin_states.items():
            state_str = "HIGH" if pin_state else "LOW"
            print(f"{pin_name}: GPIO {self.pins[pin_name]} is {state_str}")

    def cleanup(self):
        """Clean up GPIO resources."""
        print("Cleaning up PinReader GPIO")
        GPIO.cleanup()


class A4988Stepper:
    def __init__(self, pin_mappings, microstep_settings=(0, 0, 0), pin_reader=None):
        self.pins = pin_mappings
        self.pin_reader = pin_reader  # Instance of PinReader to read inputs
        
        # Set up GPIO
        for pin in self.pins.values():
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


# Set up the driver state reader
input_pin = {
    'STEP': 23,
    'ENABLED': 19,
    'MS1': 13,
    'MS2': 16,
    'MS3': 17,
    'DIR': 24
}

driver_state = PinReader(input_pin)
stepper = A4988Stepper(pin_mappings=pin_map, microstep_settings=(0,0,0), pin_reader=driver_state)

buttonPin = 27
GPIO.setup(buttonPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Main logic loop
try:
    button = 0
    steps = 0
    driver_state.print_states()
    print('Modifying direction and stepping:')
    stepper.set_direction("CW")
    stepper.set_microstepping(0, 1, 0)
    driver_state.print_states()

    while True:
        if GPIO.input(buttonPin):  # Button not pressed
            time.sleep(0.1)
        else:  # Button is pressed
            print('Button pressed')
            stepper.step()
            steps += 1
            print(f"Total steps: {steps}")
            driver_state.print_states()
            time.sleep(0.25)

except KeyboardInterrupt:
    print("Interrupted! Cleaning up...")
    stepper.cleanup()
    driver_state.cleanup()


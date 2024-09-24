import RPi.GPIO as GPIO
import time

# Define Pin Layout
GPIO.setmode(GPIO.BCM)

# # Define Pins
# ledPin = 13
# buttonPin = 27

# # Setup Pins
# GPIO.setup(ledPin, GPIO.OUT)
# GPIO.setup(buttonPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
# # pull-up means default is up, like button
# # GPIO.setwarnings(False)

# # Modify Pins

# print("Here we go!")

# try:
#     while 1:
#         if GPIO.input(buttonPin): # button is up
#             GPIO.output(ledPin, GPIO.LOW)
#             print("button up")
#         else:
#             print("button pressed")
#             GPIO.output(ledPin, GPIO.HIGH)
#             time.sleep(0.075)
#             GPIO.output(ledPin, GPIO.LOW)
#             time.sleep(0.075)
# except KeyboardInterrupt: # If CTRL+C is pressed, exit cleanly:
#     GPIO.cleanup()

# Motor setup
# driver_pins = {
#     # Control pins:
#     'EN': 22,  # pull high to deactivate (enable)
#     # Microstepping pins:
#     # Stepsize  Full    Half    Quarter Eigth   Sixteenth
#     # MS1       low     high    low     high    high
#     # MS2       low     low     high    high    high
#     # MS3       low     low     low     low     high 
#     'MS1': 4, # pull up to activate 
#     'MS2': 5, # pull up to activate
#     'MS3': 6, # pull up to activate:
#     # Optional:
#     'RESET': None,   # pull low to reset STEP inputs and return to initial driver position
#                 # connect to SLP to pull up and enable driver if not using. 
#                 # if used, employ 1 ms delay before STEP command (for charge pump stabilization)
#     'SLP': None,     # pull low to sleep
#     # Step trigger:
#     'STEP': 21, # each HIGH pulse triggers next step according to ms settings
#                 # faster pulses = faster movement
#     'DIR': 20,  # pull up for clockwise, pull down for counterclockwise
#     # The following are output/current pins:
#     'VMOT': None, 
#     'GND_MOT': None,
#     '2B': None,
#     '2A': None,
#     '1A': None,
#     '1B': None,
#     'VDD': None, 
#     'GND_PI': None,
# }

pin_map = {
    'MS1': 4, # pull up to activate 
    'MS2': 5, # pull up to activate
    'MS3': 6, # pull up to activate:
    'RESET': None,  # pull low to reset STEP inputs and return to initial driver position
                    # connect to SLP to pull up and enable driver if not using. 
                    # if used, employ 1 ms delay before STEP command (for charge pump stabilization)
    'SLP': None,    # pull low to sleep
    'STEP': 21, # each HIGH pulse triggers next step according to ms settings
                # faster pulses = faster movement
    'DIR': 20,  # pull up for clockwise, pull down for counterclockwise
    'ENABLE': 19
}

class A4988Stepper:
    def __init__(self, pin_mappings, microstep_settings=(0, 0, 0)):
        self.pins = pin_mappings
        
        # Set up GPIO
        GPIO.setmode(GPIO.BCM)  # Use BCM pin numbering
        for pin in self.pins.values():
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, GPIO.LOW)  # Set all pins to LOW initially

        # Set the initial microstepping mode
        self.set_microstepping(*microstep_settings)

    def set_pins(self, pin_name, gpio_pin):
        """Update the GPIO pin for a specific A4988 pin and reconfigure it."""
        if pin_name in self.pins:
            GPIO.setup(gpio_pin, GPIO.OUT)
            GPIO.output(gpio_pin, GPIO.LOW)  # Set to LOW initially
            self.pins[pin_name] = gpio_pin
            print(f"Updated {pin_name} pin to GPIO {gpio_pin}")
        else:
            print(f"Error: {pin_name} is not a valid A4988 pin name.")

    def set_microstepping(self, ms1=None, ms2=None, ms3=None):
        """Set microstepping mode by adjusting MS1, MS2, MS3 pins."""
        if ms1 is None and ms2 is None and ms3 is None:
            # Print the help map
            print("Microstepping Map:")
            print("Stepsize   | MS1   | MS2   | MS3")
            print("-----------|-------|-------|-------")
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
            
    def enable(self):
        """Enable the motor driver (ENABLE pin is active low)."""
        GPIO.output(self.pins['ENABLE'], GPIO.LOW)  # LOW to enable
        print(f"Motor enabled with ENABLE pin {self.pins['ENABLE']}")

    def disable(self):
        """Disable the motor driver (ENABLE pin is active low)."""
        GPIO.output(self.pins['ENABLE'], GPIO.HIGH)  # HIGH to disable
        print(f"Motor disabled with ENABLE pin {self.pins['ENABLE']}")

    def set_direction(self, direction):
        """Set direction to Clockwise (HIGH) or Counter-Clockwise (LOW)."""
        if direction == "CW":
            GPIO.output(self.pins['DIR'], GPIO.HIGH)
            print(f"Setting DIR pin {self.pins['DIR']} to HIGH for CW")
        else:
            GPIO.output(self.pins['DIR'], GPIO.LOW)
            print(f"Setting DIR pin {self.pins['DIR']} to LOW for CCW")

    def step(self):
        """Perform a single step (toggle the STEP pin)."""
        GPIO.output(self.pins['STEP'], GPIO.HIGH)
        time.sleep(0.001)  # Step pulse width (can be adjusted)
        GPIO.output(self.pins['STEP'], GPIO.LOW)
        print(f"Stepping with STEP pin {self.pins['STEP']}")

    def cleanup(self):
        """Clean up the GPIO resources when done."""
        GPIO.cleanup()
        print("GPIO cleaned up")

stepper = A4988Stepper(pin_mappings=pin_map, microstep_settings=(0,0,0))

stepper.set_direction("CW")

stepper.set_microstepping(0,1,0)

stepper.set_pins("DIR", 20)

# microstepping






# Sleep if no input

# Fwd motor motion if b1

# Rev motor motion if b2


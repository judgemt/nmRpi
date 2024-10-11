import RPi.GPIO as GPIO

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

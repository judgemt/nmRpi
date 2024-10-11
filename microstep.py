import RPi.GPIO as GPIO

class Microstep:
    def __init__(self, pins):
        # Store the GPIO pins for MS1, MS2, MS3
        self.pins = pins
        
        # Microstepping modes map
        self.MSmap = {
            'full': {'key': [0, 0, 0], 'factor': 1},
            'half': {'key': [1, 0, 0], 'factor': 2},
            'quarter': {'key': [0, 1, 0], 'factor': 4},
            'eighth': {'key': [1, 1, 0], 'factor': 8},
            'sixteenth': {'key': [1, 1, 1], 'factor': 16}
        }
        
        # Track the current mode and factor
        self.current_mode = None
        self.current_factor = None
    
    def print_msmap(self):
        """Print the available microstepping modes and their configurations."""
        print("Microstepping Map:")
        print("Mode       | MS1   | MS2   | MS3   | Factor")
        print("-----------|-------|-------|-------|--------")
        
        for mode, config in self.MSmap.items():
            ms1, ms2, ms3 = config['key']
            factor = config['factor']
            print(f"{mode:<10} | {'HIGH' if ms1 else 'LOW':<5} | {'HIGH' if ms2 else 'LOW':<5} | {'HIGH' if ms3 else 'LOW':<5} | {factor:<7}")

    def set_mode(self, mode):
        """Set the microstepping mode and configure the GPIO pins."""
        # Check if the mode exists, if not, default to 'full'
        if mode not in self.MSmap:
            print(f'Invalid stepMode {mode}. Setting to "full".')
            mode = 'full'
        
        ms_values = self.MSmap[mode]['key']
        
        # Set the MS1, MS2, MS3 pins based on the selected mode
        ms_pins = ['MS1', 'MS2', 'MS3']
        for pin_name, val in zip(ms_pins, ms_values):
            setting = GPIO.HIGH if val else GPIO.LOW
            GPIO.output(self.pins[pin_name]['number'], setting)
            print(f"Set {pin_name} to {'HIGH' if setting == GPIO.HIGH else 'LOW'}")
        
        # Track the current mode and factor
        self.current_mode = mode
        self.current_factor = self.MSmap[mode]['factor']
        
        return self.current_factor
    
    def get_mode(self):
        """Return the current microstepping mode."""
        return self.current_mode
    
    def get_factor(self):
        """Return the current steps-per-revolution factor."""
        return self.current_factor

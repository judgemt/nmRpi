import time
import RPi.GPIO as GPIO

def calibrate_step_delay(spr, speed, pulseWidth, n=1E4):
    """Calibrate the step delay, accounting for sleep overhead and pulse width."""
    
    # Calculate steps per second (SPS)
    sps = spr * speed
    start_time = time.time()

    # Measure sleep overhead
    print('Measuring sleep overhead...')
    t1 = time.time()
    for i in range(int(n)):
        time.sleep(0)  # Perform a large number of short sleep calls to measure overhead
        time.sleep(0)  # Perform a large number of short sleep calls to measure overhead
    t2 = time.time()
    
    sleep_overhead = (t2 - t1) / n  # Average sleep overhead per step
    print(f'{n} sleeps took {t2 - t1:.6f} seconds.')
    print(f'sleep_overhead =~ {sleep_overhead:.6f} seconds per step.')
    
    # Desired step time based on speed (revs per second)
    step_desired = 1 / sps
    print(f'Desired step time = {step_desired:.6f} s.')

    # Calculate the stepDelay based on desired step time, sleep overhead, and pulse width
    stepDelay = step_desired - sleep_overhead - pulseWidth
    stepDelay = round(stepDelay, 6)

    # Ensure step delay + pulse width is not below the threshold (5 µs)
    if (stepDelay + pulseWidth) < pulseWidth:
        print(f'Step duration (stepDelay + pulseWidth) must be >= pulseWidth. Current step duration is {stepDelay + pulseWidth:.6f}.')
        stepDelay = pulseWidth
        print(f"Step delay adjusted to {stepDelay:.6f} s to meet the minimum requirement.")
    else:
        print(f'Step delay adjusted to {stepDelay:.6f} seconds to account for sleep overhead.')

    return stepDelay

# Example usage:
# ms = Microstep(pin_mapping)
# speed = 1  # Example speed (revolutions per second)
# pulseWidth = 5E-6  # Example pulse width
# step_delay = calibrate_step_delay(ms, speed, pulseWidth)

def step(n, pin, pulseWidth, stepDelay):

    n = int(max(1, round(n)))

    start_time = time.time()
    
    for i in range(n):# 1 revolution
        GPIO.output(pin['STEP']['number'], GPIO.HIGH)
        time.sleep(pulseWidth)  # minimum pulse width # each of these calls costs 0.000125 s on average on an RPI4, mainly due to time.sleep overhead. Subtract this from the pulseWidth before using?
        GPIO.output(pin['STEP']['number'], GPIO.LOW)
        time.sleep(stepDelay)  # Short sleep to reduce CPU usage
    
    end_time = time.time()

    time_elapsed = end_time-start_time
    
    return time_elapsed

class Microstep:
    def __init__(self, pins, mode = 'full'):
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
        self.set_mode(mode)
    
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

import RPi.GPIO as GPIO
import subprocess
import time
import json 
import pigpio
from utils import Microstep

enable_pin = 21
BOARD_TO_BCM = {
    3: 2,  5: 3,  7: 4,  8: 14,  10: 15,
    11: 17, 12: 18, 13: 27, 15: 22, 16: 23,
    18: 24, 19: 10, 21: 9,  22: 25, 23: 11,
    24: 8,  26: 7,  29: 5,  31: 6,  32: 12,
    33: 13, 35: 19, 36: 16, 37: 26, 38: 20,
    40: 21
}

def setup_pigpio():
    # pigpio setup
    subprocess.run(["sudo","pigpio",], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) # start daemon
    time.sleep(1) # wait to give daemon a chance to start
    pi = pigpio.pi() # connect to daemon

    if not pi.connected:
        print('Failed to connect to pigpio daemon')
        exit(1)
    else:
        print('pigpio daemon started')
    
    return pi

def setup_gpio():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BOARD)

def load_pin_configurations(config_file='config/pin_map.json'):
    # Read pinmap
    with open(config_file, 'r') as file:
        pins = json.load(file)
        # print(pins)
        if pins is not None:
            print('pin configurations loaded')
            # print(json.dumps(pins, indent=4))
        else:
            print('pin configurations failed to load')
            exit(1)
    return pins

def set_enable_pin(enable_pin):
    # Set enable pin to HIGH (disabled)
    try:
        GPIO.setup(enable_pin, GPIO.OUT)
        GPIO.output(enable_pin, GPIO.HIGH) # pull up so motor isn't actively holding
        print('Enable pin set to HIGH')
    except: 
        print(f'Error: Enable pin setup failure: {enable_pin}')

def generate_pulses(step_pin_board: int, n: int, microseconds_high: int, microseconds_low: int) -> list:
    """
    Generates a list of pigpio.pulse objects for stepping.

    Args:
        step_pin_board (int): BOARD pin number for the step signal.
        n_steps (int): Number of pulses to generate.
        microseconds_high (int): Time (µs) for HIGH pulse.
        microseconds_low (int): Time (µs) for LOW pulse.

    Returns:
        list: A list of pigpio.pulse objects.
    """
    if n <= 0:
        raise ValueError("n must be greater than 0.")
    
    step_pin_bcm = BOARD_TO_BCM[step_pin_board]
    
    pulses = []
    for step in range(n):
        pulses.append(pigpio.pulse(1 << step_pin_bcm, 0, int(microseconds_high))) # HIGH
        pulses.append(pigpio.pulse(0, 1 << step_pin_bcm, int(microseconds_low)))   # LOW

    return pulses

def pulse_step(pi: pigpio.pi, step_pin_board: int, n_steps: int, microseconds_high: int = 10, microseconds_low: int = 10):
    """
    Sends a sequence of pulses to step a motor using pigpio.

    Args:
        pi (pigpio.pi): Pigpio instance.
        step_pin_board (int): BOARD pin number for stepping.
        n_steps (int): Number of pulses to generate.
        microseconds_high (int, optional): Time (µs) for HIGH pulse. Default is 10.
        microseconds_low (int, optional): Time (µs) for LOW pulse. Default is 10.

    Raises:
        ValueError: If `n_steps` is <= 0.
    """
    pi.exceptions = True
    
    pulses = generate_pulses(step_pin_board, n_steps, microseconds_high, microseconds_low)

    pi.wave_clear()               # Clear existing waveforms
    pi.wave_add_generic(pulses)   # Add new waveform
    wave_id = pi.wave_create()    # Create waveform

    if wave_id < 0:
        raise RuntimeError("Failed to create waveform.")

    pi.wave_send_once(wave_id)    # Send waveform

    while pi.wave_tx_busy():      # Wait for transmission to complete
        time.sleep(0.001)

    pi.wave_clear()               # Cleanup waveforms

def setup_gpio_pin(pin, pin_name):
    try:
        initial_state = GPIO.LOW if pin['init'] == "LOW" else GPIO.HIGH
        GPIO.setup(pin['number'], GPIO.OUT)
        GPIO.output(pin['number'], initial_state)
        print(f'{pin_name} pin set up at board pin:',pin['number'])
        
    except: 
        print(f'{pin_name} failed setup')

def setup_pigpio_pin(pi: pigpio.pi, pin, pin_name):
    try:
        if pin_name == "STEP":
            step_pin = BOARD_TO_BCM[pin['number']] # pigpio assumes BCM numbering
            print('Setting STEP pin on BCM pin ',step_pin,' up with pigpio')
            pi.set_mode(step_pin, pigpio.OUTPUT)
            # print('mode set..')
            pi.set_pull_up_down(step_pin, pigpio.PUD_DOWN)
            # print('pulldown set..')
            print('STEP pin was set with internal pulldown.')

    except: 
        print(f'{pin_name} failed setup')
    
def setup_pins(pins, pi):
    for pin_name, pin in pins.items():
        if pin_name == "STEP":
            setup_pigpio_pin(pi, pin, pin_name)
        else:
            setup_gpio_pin(pin, pin_name)
    print("Pin setup complete")

def cleanup_pins(pi):
    GPIO.cleanup()
    pi.stop()

def set_direction(direction):
    if direction is "Clockwise":
        GPIO.output(pins['DIR']['number'], GPIO.LOW)
        print('Direction set to "Clockwise"')
    elif direction is "Counterclockwise":
        GPIO.output(pins['DIR']['number'], GPIO.HIGH)
        print('Direction set to "Counterclockwise"')
    else:
        RuntimeError(f'Direction "{direction}" should be "Clockwise" or "Counterclockwise".')


## Setup ##############################

pins = load_pin_configurations()
pi = setup_pigpio()    
setup_gpio()
set_enable_pin(enable_pin)
setup_pins(pins, pi)
microstep = Microstep(pins, mode = 'full')

try: 

    microstep.set_mode('sixteenth')
    set_direction('Counterclockwise')
    GPIO.output(enable_pin, GPIO.LOW) # pull down *motor will actively hold*
    print('enable pin activated')
    pulse_step(pi,
                pins['STEP']['number'], 
                n_steps=50*microstep.get_factor(), 
                microseconds_high=10, 
                microseconds_low=1e4) # this uses board numbering
    print('steps complete')

except Exception as e:
    print(f"Error: {e}")
    cleanup_pins(pi)
    print('Driver inactive')
    exit(1)

cleanup_pins(pi)
print('Driver inactive')
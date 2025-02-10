import RPi.GPIO as GPIO
import subprocess
import time
import json 
import pigpio
from utils import Microstep

config_file = 'config/pin_map.json'
enable_pin = 21

# pigpio setup
subprocess.run(["sudo","pigpio",], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) # start daemon
time.sleep(1) # wait to give daemon a chance to start
pi = pigpio.pi() # connect to daemon

if not pi.connected:
    print('Failed to connect to pigpio daemon')
    exit(1)
else:
    print('pigpio daemon started')
 
#  Test stepping

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
BOARD_TO_BCM = {
    3: 2,  5: 3,  7: 4,  8: 14,  10: 15,
    11: 17, 12: 18, 13: 27, 15: 22, 16: 23,
    18: 24, 19: 10, 21: 9,  22: 25, 23: 11,
    24: 8,  26: 7,  29: 5,  31: 6,  32: 12,
    33: 13, 35: 19, 36: 16, 37: 26, 38: 20,
    40: 21
}

# Read pinmap
with open(config_file, 'r') as file:
    pins = json.load(file)
    # print(pins)
    if pins is not None:
        print('pin configurations loaded:')
        # print(json.dumps(pins, indent=4))
    else:
        print('pin configurations failed to load')
        exit(1)

# Set enable pin to HIGH (disabled)
try:
    GPIO.setup(enable_pin, GPIO.OUT)
    GPIO.output(enable_pin, GPIO.HIGH) # pull up so motor isn't actively holding
    print('Enable pin set to HIGH')
except: 
    print(f'Error: Enable pin setup failure: {enable_pin}')

def pulse_step(step_pin_board, n_steps, microseconds_high=10, microseconds_low=10):
    
    # Generate the list of pulses
    pulses = []
    
    step_pin_bcm = BOARD_TO_BCM[step_pin_board]
    print('generating pulse:')
    for step in range(n_steps):
        pulses.append(pigpio.pulse(1<<step_pin_bcm, 0,              int(microseconds_high)))
        pulses.append(pigpio.pulse(0,           1<<step_pin_bcm,    int(microseconds_low)))

    # Visualize

    pi.exceptions = True

    # Turn into a pigpio waveform
    pi.wave_clear()             # just in case something is running
    time.sleep(0.1)
    pi.wave_add_generic(pulses) # make the wave from the pulses
    wave_id = pi.wave_create()

    # Send the wave to hardware
    pi.wave_send_once(wave_id)  # send it

    # Give the wave time to run
    while pi.wave_tx_busy():    
        time.sleep(0.001)       # check in every millisecond

    pi.wave_clear() # Clean up waveform

def setup_pin(pin, pin_name):
    try:
        if pin_name == "STEP":
            step_pin = BOARD_TO_BCM[pin['number']] # pigpio assumes BCM numbering
            print('Setting STEP pin on BCM pin ',step_pin,' up with pigpio')
            pi.set_mode(step_pin, pigpio.OUTPUT)
            # print('mode set..')
            pi.set_pull_up_down(step_pin, pigpio.PUD_DOWN)
            # print('pulldown set..')
            print('STEP pin was set with internal pulldown.')
        else:
            initial_state = GPIO.LOW if pin['init'] == "LOW" else GPIO.HIGH
            GPIO.setup(pin['number'], GPIO.OUT)
            GPIO.output(pin['number'], initial_state)
            print(f'{pin_name} pin set up at board pin:',pin['number'])
        
    except: 
        print(f'{pin_name} failed setup')
    
for pin_name, pin in pins.items():
    setup_pin(pin, pin_name) 

def cleanup_pins():
    GPIO.output(enable_pin, GPIO.HIGH) # 
    # # Shutdown
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
    

#### Do Stuff #####

# Turn driver on

microstep = Microstep(pins, mode = 'full')

try: 

    microstep.set_mode('sixteenth')
    set_direction('Counterclockwise')
    GPIO.output(enable_pin, GPIO.LOW) # pull down *motor will actively hold*
    print('enable pin activated')
    pulse_step(pins['STEP']['number'], 
                n_steps=50*microstep.get_factor(), 
                microseconds_high=10, 
                microseconds_low=1e4) # this uses board numbering
    print('did the steps')

except Exception as e:
    print(f"Error: {e}")
    cleanup_pins()

cleanup_pins()
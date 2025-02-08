import RPi.GPIO as GPIO
import subprocess
import time
import json 
import pigpio

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

def pulse_step(step_pin, n_steps, microseconds_high=10, microseconds_low=10):
    
    # Generate the list of pulses
    pulses = []
    
    for step in range(n_steps):
        pulses.append(pigpio.pulse(1<<step_pin, 0,              microseconds_high))
        pulses.append(pigpio.pulse(0,           1<<step_pin,    microseconds_low))

    # Turn into a pigpio waveform
    pi.wave_clear()             # just in case something is running
    pi.wave_add_generic(pulses) # make the wave from the pulses
    wave_id = pi.wave_create()  # 

    # Send the wave to hardware
    pi.wave_send_once(wave_id)  # send it

    # Give the wave time to run
    while pi.wave_tx_busy():    
        time.sleep(0.001)       # check in every millisecond

    pi.wave_clear() # Clean up waveform

def setup_pin(pin, pin_name):
    try:
        if pin_name == "STEP":
            print('Setting STEP pin up with pigpio')
            step_pin = pin['number']
            print(step_pin)
            pi.set_mode(step_pin, pigpio.OUTPUT)
            print('mode set..')
            pi.set_pull_up_down(step_pin, pigpio.PUD_DOWN)
            print('pulldown set..')
        else:
            initial_state = GPIO.LOW if pin['init'] == "LOW" else GPIO.HIGH
            GPIO.setup(pin['number'], GPIO.OUT)
            GPIO.output(pin['number'], initial_state)
            print(f'{pin_name} pin set up at board pin:',pin['number'])
        
    except: 
        print(f'{pin_name} failed setup')
    
for pin_name, pin in pins.items():
    setup_pin(pin, pin_name) 

# print(pin['STEP']['number'])
# pulse_step(pin['STEP']['number'])

#### Do Stuff #####

# Turn driver on
# GPIO.output(enable_pin, GPIO.LOW) # pull down *motor will actively hold*

# # Shutdown
GPIO.cleanup()
pi.stop()
 
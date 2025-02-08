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
    print(pins)
    if pins is not None:
        print('pin configurations loaded:')
        print(json.dumps(pins, indent=4))
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

def setup_pin(pin, pin_name):
    try:
        initial_state = GPIO.LOW if pin['init'] == "LOW" else GPIO.HIGH
        GPIO.setup(pin['number'], GPIO.OUT)
        GPIO.output(pin['number'], initial_state)
        print(f'{pin_name} pin set up at board pin:',pin['number'])
        
    except: 
        print(f'{pin_name} failed setup')

for pin_name, pin in pins.items():
    setup_pin(pin, pin_name)
    


#### Do Stuff #####

# Turn driver on
# GPIO.output(enable_pin, GPIO.LOW) # pull down *motor will actively hold*

# Loop a little
# for i in range(200):
#     pi.write(step_pin, 1)
#     pi.time_sleep(0.0001)
#     pi.write(step_pin, 0)
#     pi.time_sleep(0.0001)

# # Shutdown
GPIO.cleanup()
pi.stop()
 
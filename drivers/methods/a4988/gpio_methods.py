import RPi.GPIO as GPIO
import json
from .pigpio_methods import setup_pigpio_pin, require_valid_pi as check_pi

def setup_gpio():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BOARD)

def load_pin_configurations(config_file):
    try:
        # Read pinmap
        with open(config_file, 'r') as file:
            pins = json.load(file)
            print("Driver Pin Configurations:")
            print(pins)
            if pins is not None:
                print('pin configurations loaded')
                # print(json.dumps(pins, indent=4))p
            else:
                print('pin configurations failed to load')
                exit(1)
        return pins
    except Exception as e:
        print(f"Error in load_pin_configurations: {e}")
        return None

def setup_enable_pin(pin):
    # Set enable pin to HIGH (disabled)
    try:
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, GPIO.HIGH) # pull up so motor isn't actively holding
        print(f'Enable pin {pin} set to HIGH')
    except: 
        print(f'Error: Enable pin setup failure: {pin}')

def setup_enable_pins(enable_pins):
    try:
        # Set enable pin to HIGH (disabled)
        for pin in enable_pins:
            setup_enable_pin(pin)
    except Exception as e:
        print('Error during setup_enable_pins: {e}.')
        print('Check enable pin assignments and/or GPIO status.')
        exit(1)
        
def setup_gpio_pin(pin, pin_name):
    try:
        initial_state = GPIO.LOW if pin['init'] == "LOW" else GPIO.HIGH
        GPIO.setup(pin['number'], GPIO.OUT)
        GPIO.output(pin['number'], initial_state)
        print(f'{pin_name} pin set up at board pin:',pin['number'])
        
    except: 
        print(f'{pin_name} failed setup')

def setup_shared_pins(pins, pi):
    setup_gpio()
    for pin_name, pin in pins.items():
        if pin_name == "STEP":
            setup_pigpio_pin(pi, pin, pin_name)
        else:
            setup_gpio_pin(pin, pin_name)
    print("Pin setup complete")

@check_pi
def cleanup_pins(pi):
    GPIO.cleanup()
    pi.stop()

def enable(enable_pins, pin_index):
    # Disable all others
    disable_all(enable_pins)
    
    # Enable the desired pin
    GPIO.output(enable_pins[pin_index], GPIO.LOW) # pull down *motor will actively hold*
    print(f'Driver {pin_index} at physical pin {enable_pins[pin_index]} is enabled.')

def disable_all(enable_pins):
    # Disable all
    for pin in enable_pins:
        disable(pin)
    print(f'Enable pins {enable_pins} were disabled')
    
def disable(pin):
    GPIO.output(pin, GPIO.HIGH) # pull down *motor will actively hold*


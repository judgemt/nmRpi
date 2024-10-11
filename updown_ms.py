import RPi.GPIO as GPIO
import time
from microstep import Microstep

# Main script

GPIO.setmode(GPIO.BCM)

# Define pin layout

pin = {
    'DIR': {'number': 27, 'init': GPIO.LOW},
    'STEP': {'number': 26, 'init': GPIO.LOW},
    'SLP': {'number': 25, 'init': GPIO.LOW},
    'MS3': {'number': 23, 'init': GPIO.LOW},
    'MS2': {'number': 22, 'init': GPIO.LOW},
    'MS1': {'number': 21, 'init': GPIO.LOW},
    'ENABLE': {'number': 20, 'init': GPIO.HIGH},
}

revolutions = 1
stepMode = "sixteenth"
speed = 1 # revs per second
pulseWidth = 5E-6

# Set up pins

for name, info in pin.items():
    GPIO.setup(info['number'], GPIO.OUT)
    print(f"{name} assigned to GPIO pin {info['number']}")

# Initialize pins

for name, info in pin.items():
    GPIO.output(info['number'], info['init'])
    print(f"{name} set to {info['init']}")

# Set step mode

ms = Microstep(pin)
ms.set_mode(stepMode)
spr = ms.get_factor() * 200
stepDelay = 1/spr

# Main logic loop

print("Main loop:")
step = 0
print(f"stepDelay = {stepDelay}")

try:
    GPIO.output(pin['ENABLE']['number'], GPIO.LOW)
    GPIO.output(pin['SLP']['number'], GPIO.HIGH)
    print('Driver enabled')

    print(f'Running in {revolutions} turns:')
    GPIO.output(pin['DIR']['number'], GPIO.HIGH)

    for i in range(spr*revolutions):# 1 revolution
        step += 1
        # print('Button pressed, stepping motor')
        GPIO.output(pin['STEP']['number'], GPIO.HIGH)
        # print(f"Total steps: {step}")
        time.sleep(pulseWidth)  # minimum pulse width
        GPIO.output(pin['STEP']['number'], GPIO.LOW)
        time.sleep(pulseWidth)  # minimum pulse width
        
        time.sleep(stepDelay)  # Short sleep to reduce CPU usage

    print('Pausing 1 sec...')
    time.sleep(1)
    
    print(f'Running out {revolutions} turns:')
    GPIO.output(pin['DIR']['number'], GPIO.LOW)
    for i in range(spr*revolutions):# 1 revolution
        step += 1
        # print('Button pressed, stepping motor')
        GPIO.output(pin['STEP']['number'], GPIO.HIGH)
        # print(f"Total steps: {step}")
        time.sleep(pulseWidth)  # minimum pulse width
        GPIO.output(pin['STEP']['number'], GPIO.LOW)
        time.sleep(pulseWidth)  # minimum pulse width
        
        time.sleep(stepDelay)  # Short sleep to reduce CPU usage
    
    GPIO.output(pin['SLP']['number'], GPIO.LOW)
    GPIO.output(pin['ENABLE']['number'], GPIO.HIGH)
    

    # GPIO.output(pin['ENABLE']['number'], GPIO.HIGH)
    print('Driver disabled')

except KeyboardInterrupt():
    print('Exiting')
finally:
    print('done')
    # GPIO.cleanup() # if cleanup, GPIO resets and motor will freeze/jitter.
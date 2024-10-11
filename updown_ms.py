import RPi.GPIO as GPIO
import time
from microstep import Microstep
from utils import calibrate_step_delay
from utils import step

# Main script

GPIO.setmode(GPIO.BCM)

# Define pin layout

pin = {
    'DIR': {'number': 27, 'init': GPIO.LOW},
    'STEP': {'number': 26, 'init': GPIO.LOW},
    'MS3': {'number': 23, 'init': GPIO.LOW},
    'MS2': {'number': 22, 'init': GPIO.LOW},
    'MS1': {'number': 21, 'init': GPIO.LOW},
    'ENABLE': {'number': 20, 'init': GPIO.HIGH},
}

revolutions = 3
stepMode = "sixteenth"
speed = 2 # revs per second
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
n = spr*revolutions

stepDelay = calibrate_step_delay(spr, speed, pulseWidth, 5E4)

# Main logic loop

print("Main loop:")

try:
    GPIO.output(pin['ENABLE']['number'], GPIO.LOW)
    print('Driver enabled')
    print(f'Running in {revolutions} turns:')
    GPIO.output(pin['DIR']['number'], GPIO.HIGH)

    time_elapsed = step(n, pin, pulseWidth, stepDelay)
    print(f"Speed measured @ {round(revolutions/time_elapsed, 3)} rps")

    print('Pausing 1 sec...')

    time.sleep(1)
    
    print(f'Running out {revolutions} turns:')
    GPIO.output(pin['DIR']['number'], GPIO.LOW)

    time_elapsed = step(n, pin, pulseWidth, stepDelay)
    print(f"Speed measured @ {round(revolutions/time_elapsed, 3)} rps")
    
    GPIO.output(pin['ENABLE']['number'], GPIO.HIGH)
    print('Driver disabled')

except KeyboardInterrupt():
    print('Exiting')
finally:
    print('done')
    # GPIO.cleanup() # if cleanup, GPIO resets and motor will freeze/jitter.
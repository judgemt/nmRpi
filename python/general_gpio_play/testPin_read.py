import RPi.GPIO as GPIO
import time

# Define Pin Layout
GPIO.setmode(GPIO.BCM)

# Define Pins
# set pins connected to each other with resistor between.
outPin = 27
inPin = 13

# print(f"testing outPin {outPin}")
# # Setup Pins
# GPIO.setup(outPin, GPIO.OUT)
# GPIO.output(outPin, GPIO.HIGH)

GPIO.setup(outPin, GPIO.OUT) 

print(f"testing PUD_UP for inPin {inPin}")

GPIO.setup(inPin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
print(f'Pin {inPin} started')
print(GPIO.input(inPin))
GPIO.output(outPin, GPIO.HIGH)
print(f'Pin {inPin} is now')
print(GPIO.input(inPin))

if GPIO.input(inPin):
    print(f'Pin {inPin} was pulled UP')
else:
    print(f'Pin {inPin} pull UP failed***')

time.sleep(1)

print(f"testing PUD_UP for inPin {inPin}")

GPIO.setup(inPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
print(f'Pin {inPin} started')
print(GPIO.input(inPin))
print(GPIO.input(inPin))
GPIO.output(outPin, GPIO.LOW)
print(f'Pin {inPin} is now')
print(GPIO.input(inPin))
if not GPIO.input(inPin):
    print(f'Pin {inPin} was pulled DOWN')
else:
    print(f'Pin {inPin} pull DOWN failed***')

time.sleep(1)

GPIO.cleanup()
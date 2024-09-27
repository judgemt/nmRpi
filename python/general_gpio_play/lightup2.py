import RPi.GPIO as GPIO
import time

# Define Pin Layout
GPIO.setmode(GPIO.BCM)

# Define Pins
ledPin = 27

# Setup Pins
GPIO.setup(ledPin, GPIO.OUT)
# GPIO.setwarnings(False)

try:
    while 1:
        # Modify Pins
        print("LED on")
        GPIO.output(ledPin, GPIO.HIGH)
        time.sleep(1)
        print("LED off")
        GPIO.output(ledPin, GPIO.LOW)
        time.sleep(.5)
except KeyboardInterrupt:
    GPIO.cleanup()
import RPi.GPIO as GPIO
import time

# Define Pin Layout
GPIO.setmode(GPIO.BCM)

# Define Pins
ledPin = 17

# Setup Pins
GPIO.setup(ledPin, GPIO.OUT)
# GPIO.setwarnings(False)

# Modify Pins
print("LED on")
GPIO.output(ledPin, GPIO.HIGH)
time.sleep(1)
print("LED off")
GPIO.output(ledPin, GPIO.LOW)

GPIO.cleanup

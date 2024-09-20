import RPi.GPIO as GPIO
import time

# This script will allow you to push two buttons - one for each of two LEDs.
# Only one can be on at a time. If an LED is on, and another gets activated, turn off the first one. 

# Pins
GPIO.setmode(GPIO.BCM)
led1 = 17
led2 = 16

but1 = 26
but2 = 27
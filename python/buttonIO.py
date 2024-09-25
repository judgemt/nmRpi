import RPi.GPIO as GPIO
import time

# Define Pin Layout
GPIO.setmode(GPIO.BCM)

# Define Pins
ledPin = 13
buttonPin = 18

# Setup Pins
GPIO.setup(ledPin, GPIO.OUT)
GPIO.setup(buttonPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
# pull-up means default is up, like button
# GPIO.setwarnings(False)

# Modify Pins

print("Here we go!")

try:
    while 1:
        time.sleep(0.1)
        if GPIO.input(buttonPin): # button is up
            GPIO.output(ledPin, GPIO.LOW)
            print("button up")
        else:
            print("button pressed")
            GPIO.output(ledPin, GPIO.HIGH)
            time.sleep(0.075)
            GPIO.output(ledPin, GPIO.LOW)
            time.sleep(0.075)
except KeyboardInterrupt: # If CTRL+C is pressed, exit cleanly:
    GPIO.cleanup()
    

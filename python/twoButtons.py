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

GPIO.setup(led1, GPIO.OUT)
GPIO.setup(led2, GPIO.OUT)
GPIO.setup(but1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(but2, GPIO.IN, pull_up_down=GPIO.PUD_UP)

print("Press and hold buttons")

try:
    while 1:
        time.sleep(0.25)
        if GPIO.input(but1) and GPIO.input(but2):
            GPIO.output
        if GPIO.input(but1): # button is up
            print("button 1 off")
            GPIO.output(led1, GPIO.LOW)
        else: 
            print("button 1 pressed")
            GPIO.output(led1, GPIO.HIGH)
        if GPIO.input(but2): # button is up
            print("button 2 off")
            GPIO.output(led2, GPIO.LOW)
        else: 
            print("button 2 pressed")
            GPIO.output(led2, GPIO.HIGH)

        # print("cycle")
        # if GPIO.input(but1) or not GPIO.input(but2): # button is up
        #     GPIO.output(led1, GPIO.LOW)
        # else: 
        #     print("button 1 pressed")
        #     GPIO.output(led1, GPIO.HIGH)
        #     GPIO.output(led2, GPIO.LOW)
        # if GPIO.input(but2) or not GPIO.input(but1):
        #     GPIO.output(led2, GPIO.LOW)
        # else: 
        #     print("button 2 pressed")
        #     GPIO.output(led2, GPIO.HIGH)
        #     GPIO.output(led1, GPIO.LOW)
except KeyboardInterrupt: # If CTRL+C is pressed, exit cleanly:
    GPIO.cleanup()

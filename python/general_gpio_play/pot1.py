import RPi.GPIO as GPIO
import time

# The Goal of this program is to use a potentiometer and led to make a dimmer light
# There are no analog pins on an RPi, so a 22uF capacitor is needed in order to simulate an ADC. 
# Setup
GPIO.setmode(GPIO.BCM) # using piwedge
potPin = 18
ledPin = 17

GPIO.setup(potPin, GPIO.IN)
GPIO.setup(ledPin, GPIO.OUT)

pwm = GPIO.PWM(potPin, 1000)
pwm.start(0)

try:
    while 1:
        pot_value = GPIO.input(potPin)
        pot_pct = pot_value / 1023 * 100
        print(pot_pct)
        time.sleep(0.1)
except KeyboardInterrupt:
    pass

pwm.stop()
GPIO.cleanup()
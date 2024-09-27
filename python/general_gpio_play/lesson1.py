import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)

GPIO.setup(18, GPIO.OUT)

GPIO.output(18, GPIO.HIGH)

pwm = GPIO.PWM(18, 1000)
pwm.start(50)

GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP)

time.sleep(0.25)

GPIO.cleanup()
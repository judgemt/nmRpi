import RPi.GPIO as GPIO
import subprocess
import time

import pigpio

# pigpio setup
subprocess.run(["sudo","pigpio",], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) # start daemon
time.sleep(1) # wait to give daemon a chance to start
pi = pigpio.pi() # connect to daemon

if not pi.connected:
    print('Failed to connect to pigpio daemon')
    exit(1)

#  
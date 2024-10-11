import RPi.GPIO as GPIO
import time

# Main script

GPIO.setmode(GPIO.BCM)


# Define pin layout
stepPin = 16

GPIO.setup(stepPin, GPIO.OUT)
GPIO.output(stepPin, GPIO.LOW)  # Set all pins to LOW initially

step = 0

# Main logic loop

try:
    for i in range(200):# 1 revolution
        step += 1
        # print('Button pressed, stepping motor')
        GPIO.output(stepPin, GPIO.HIGH)
        print(f"Total steps: {step}")
        time.sleep(0.005)  # Debounce the button
        GPIO.output(stepPin, GPIO.LOW)
        time.sleep(0.005)  # Short sleep to reduce CPU usage
except KeyboardInterrupt():
    print('Exiting')
finally:
    GPIO.cleanup()
    print("GPIO cleanup complete")

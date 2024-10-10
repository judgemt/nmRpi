import RPi.GPIO as GPIO
import time

# Main script

GPIO.setmode(GPIO.BCM)


# Define pin layout
stepPin = 16

GPIO.setup(stepPin, GPIO.OUT)
GPIO.output(stepPin, GPIO.LOW)  # Set all pins to LOW initially

# Main logic loop

print('Button pressed, stepping motor')
GPIO.output(stepPin, GPIO.HIGH)
print(f"Total steps: ")
time.sleep(0.25)  # Debounce the button
GPIO.output(stepPin, GPIO.LOW)
time.sleep(0.1)  # Short sleep to reduce CPU usage

GPIO.cleanup()
print("GPIO cleanup complete")

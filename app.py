from flask import Flask, render_template, redirect, url_for
import RPi.GPIO as GPIO
import time
from drivers.stepper import A4988
from drivers.pump_v0 import Pump

app = Flask(__name__)

# Define the pump initialization here, so it's ready for use in the app
def initialize_pump():
    # Initialize the A4988 motor object
    stepper = A4988(config_file='config/pin_map.json', auto_calibrate=True, speed=.5, pulseWidth=5E-6)
    
    # Initialize the Pump object
    pump = Pump(motor=stepper, syringe_volume=4, ml_per_rotation=4.5/5, step_mode='sixteenth')
    return pump

# Initialize the pump when the app starts
pump = initialize_pump()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/run_pump')
def run_pump():
    try:
        pump.move_volume(2, speed=.5)  # Run the pump command
        return redirect(url_for('index'))  # Redirect to home page after running
    except Exception as e:
        print(f"Error running pump: {e}")
        return "An error occurred while running the pump."

# Clean up GPIO when the app shuts down
@app.teardown_appcontext
def cleanup_gpio(exception):
    pump.motor.disable()
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

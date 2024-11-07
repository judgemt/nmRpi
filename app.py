from flask import Flask, render_template, request, redirect, url_for
import RPi.GPIO as GPIO
import time
from datetime import datetime
from drivers.stepper import A4988
from drivers.pump_v0 import Pump

app = Flask(__name__)

# Initialize log to store pump actions
log = []

# Define the pump initialization here, so it's ready for use in the app
def initialize_pump():
    stepper = A4988(config_file='config/pin_map.json', auto_calibrate=True, speed=0.5, pulseWidth=5E-6)
    pump = Pump(motor=stepper, syringe_volume=5, ml_per_rotation=1, step_mode='sixteenth')
    return pump

# Initialize the pump when the app starts
pump = initialize_pump()

@app.route('/')
def index():
    # Render the page without a pre-filled volume initially
    return render_template('index.html', last_volume="", last_speed=0.5, log=log)

@app.route('/run_pump', methods=['POST'])
def run_pump():
    try:
        # Get volume and speed from the form input
        volume = float(request.form['volume'])
        speed = float(request.form['speed'])
        
        # Run the pump command with the specified volume and speed
        pump.move_volume(volume, speed=speed)
        
        # Calculate flow rate in mL/s
        flow_rate = speed * pump.ml_per_rotation
        
        # Create a timestamped log entry
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"{timestamp}: Moved {volume} mL at flow rate {flow_rate:.2f} mL/s"
        log.append(log_entry)
        print(log_entry)
        
        # Pass last inputs and log to template
        return render_template('index.html', last_volume=volume, last_speed=speed, log=log)
    
    except Exception as e:
        error_message = f"Error running pump: {e}"
        print(error_message)
        log.append(error_message)
        return render_template('index.html', last_volume="", last_speed=0.5, log=log)

# Disable the motor when the app context shuts down
@app.teardown_appcontext
def disable_motor(exception):
    pump.motor.disable()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

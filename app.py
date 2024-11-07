from flask import Flask, render_template, request, redirect, url_for
import RPi.GPIO as GPIO
import time
from datetime import datetime
from drivers.stepper import A4988
from drivers.pump_v0 import Pump

app = Flask(__name__)

# Initialize log to store pump actions
log = []

# Global variable for pump settings
pump_settings = {
    'syringe_volume': 5.0,
    'ml_per_rotation': 1.0,
    'step_mode': 'sixteenth',
    'speed': 0.5
}

# Function to initialize the pump
def initialize_pump(settings):
    stepper = A4988(config_file='config/pin_map.json', auto_calibrate=True, speed=settings['speed'], pulseWidth=5E-6)
    pump = Pump(
        motor=stepper,
        syringe_volume=settings['syringe_volume'],
        ml_per_rotation=settings['ml_per_rotation'],
        step_mode=settings['step_mode']
    )
    return pump

# Initialize the pump when the app starts
pump = initialize_pump(pump_settings)

@app.route('/')
def index():
    return render_template('index.html', last_volume="", last_speed=0.5, log=log)

@app.route('/setup')
def setup():
    return render_template('setup.html', settings=pump_settings)

@app.route('/run_pump', methods=['POST'])
def run_pump():
    try:
        volume = float(request.form['volume'])
        speed = float(request.form['speed'])
        
        # Run the pump command with the specified volume and speed
        pump.move_volume(volume, speed=speed)
        
        # Calculate flow rate and log
        flow_rate = speed * pump.ml_per_rotation
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"{timestamp}: Moved {volume} mL at flow rate {flow_rate:.2f} mL/s"
        log.append(log_entry)
        
        return render_template('index.html', last_volume=volume, last_speed=speed, log=log)
    
    except Exception as e:
        error_message = f"Error running pump: {e}"
        log.append(error_message)
        return render_template('index.html', last_volume="", last_speed=0.5, log=log)

@app.route('/setup_pump', methods=['POST'])
def setup_pump():
    try:
        # Update pump settings with form inputs
        pump_settings['syringe_volume'] = float(request.form['syringe_volume'])
        pump_settings['ml_per_rotation'] = float(request.form['ml_per_rotation'])
        pump_settings['step_mode'] = request.form['step_mode']
        pump_settings['speed'] = float(request.form['speed'])
        
        # Reinitialize the pump with new settings
        global pump
        pump = initialize_pump(pump_settings)
        
        # Log the setup action
        setup_log = f"Pump reconfigured with: syringe_volume={pump_settings['syringe_volume']} mL, " \
                    f"ml_per_rotation={pump_settings['ml_per_rotation']} mL, " \
                    f"step_mode={pump_settings['step_mode']}, speed={pump_settings['speed']} rps"
        log.append(setup_log)
        
        return redirect(url_for('index'))
    
    except Exception as e:
        error_message = f"Error setting up pump: {e}"
        log.append(error_message)
        return redirect(url_for('setup'))

@app.teardown_appcontext
def disable_motor(exception):
    pump.motor.disable()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

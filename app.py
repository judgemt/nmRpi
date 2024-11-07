from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import RPi.GPIO as GPIO
import time
import re
import json
import os
import threading
from datetime import datetime
from drivers.stepper import A4988
from drivers.pump_v0 import Pump

app = Flask(__name__)

app.secret_key = 'your_secret_key'  # Required for flash messages

# Initialize log to store pump actions
log = []

# Directory to store program files
PROGRAMS_DIR = 'programs'
if not os.path.exists(PROGRAMS_DIR):
    os.makedirs(PROGRAMS_DIR)

# event stuff
is_paused = threading.Event()
is_running = False

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
    # Retrieve last volume and speed from flashed messages, if available
    last_volume = request.args.get('last_volume', "")
    last_speed = request.args.get('last_speed', 0.5)
    return render_template('index.html', last_volume=last_volume, last_speed=last_speed, log=log)

@app.route('/run_pump', methods=['POST'])
def run_pump():
    try:
        # Get volume and speed from the form input
        volume = float(request.form['volume'])
        speed = float(request.form['speed'])
        
        # Run the pump command with the specified volume and speed
        pump.move_volume(volume, speed=speed)
        
        # Log entry (optional)
        log.append(f"Moved {volume} mL at {speed} rps.")
        
        # Redirect with the last inputs as query parameters to avoid resubmission
        return redirect(url_for('index', last_volume=volume, last_speed=speed))
    
    except Exception as e:
        print(f"Error running pump: {e}")
        log.append(f"Error running pump: {e}")
        return redirect(url_for('index'))  # Redirect to avoid repeated errors on refresh
    
@app.route('/setup')
def setup():
    return render_template('setup.html', settings=pump_settings)
    
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

@app.route('/program_editor')
def program_editor():
    """Displays a simple text box for editing a program."""
    return render_template('program_editor.html')

# Define patterns for parsing each command
COMMANDS = {
    'MOVE': r'^MOVE (\d+(\.\d+)?)\s*(ml)?\s*SPEED (\d+(\.\d+)?)\s*(ml/s)?$',
    'PAUSE': r'^PAUSE (\d+(\.\d+)?)$',
    'END': r'^END$'
}

def parse_command(command):
    """Parse a command line and return the action and values if valid."""
    for action, pattern in COMMANDS.items():
        match = re.match(pattern, command)
        if match:
            if action == "MOVE":
                volume = float(match.group(1))
                speed = float(match.group(4))
                return action, volume, speed
            elif action == "PAUSE":
                duration = float(match.group(1))
                return action, duration
            elif action == "END":
                return action, None
    return None, None, None

@app.route('/save_program', methods=['POST'])
def save_program():
    """Saves the program content under the specified name and redirects back to the main page."""
    program_name = request.form['program_name']
    program_content = request.form['program_content']
    
    # Ensure the program name is a valid filename
    safe_program_name = "".join([c for c in program_name if c.isalpha() or c.isdigit() or c == ' ']).rstrip()
    program_file = os.path.join(PROGRAMS_DIR, f"{safe_program_name}.json")

    # Save the program content to a file with the specified name
    with open(program_file, 'w') as file:
        json.dump({'name': program_name, 'content': program_content}, file)

    # Redirect back to the main page with a flash message
    flash(f"Program '{program_name}' saved successfully.")
    return redirect(url_for('index'))

@app.route('/run_program')
def run_program():
    """Displays the Run Program page."""
    programs = [f.replace('.json', '') for f in os.listdir(PROGRAMS_DIR) if f.endswith('.json')]
    return render_template('run_program.html', programs=programs, log=log)

@app.route('/load_program', methods=['POST'])
def load_program():
    """Loads and displays a selected program."""
    program_name = request.form['program_name']
    program_file = os.path.join(PROGRAMS_DIR, f"{program_name}.json")
    
    if os.path.exists(program_file):
        with open(program_file, 'r') as file:
            program_data = json.load(file)
        return jsonify({'content': program_data['content']})
    else:
        return jsonify({'error': 'Program not found'}), 404

def execute_program(program_content):
    """Runs the program, with the option to pause and resume."""
    global is_running
    is_running = True
    log.clear()
    
    for line in program_content.splitlines():
        if not is_running:
            break
        is_paused.wait()  # Wait here if paused
        command = line.strip()
        log.append(f"Executing: {command}")
        print(f"Executing: {command}")  # For debugging; replace with actual execution logic
        time.sleep(1)  # Simulate action duration
        
    is_running = False
    log.append("Program execution complete.")

@app.route('/start_program', methods=['POST'])
def start_program():
    """Starts executing the loaded program in a separate thread."""
    program_content = request.form['program_content']
    thread = threading.Thread(target=execute_program, args=(program_content,))
    thread.start()
    return jsonify({'status': 'started'})

@app.route('/pause_program', methods=['POST'])
def pause_program():
    """Pauses the program execution."""
    is_paused.clear()  # Pause the thread
    return jsonify({'status': 'paused'})

@app.route('/resume_program', methods=['POST'])
def resume_program():
    """Resumes the program execution."""
    is_paused.set()  # Resume the thread
    return jsonify({'status': 'resumed'})

@app.route('/stop_program', methods=['POST'])
def stop_program():
    """Stops the program execution."""
    global is_running
    is_running = False
    is_paused.set()  # Resume to allow thread to exit if paused
    return jsonify({'status': 'stopped'})

@app.teardown_appcontext
def disable_motor(exception):
    pump.motor.disable()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

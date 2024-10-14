from flask import Flask, render_template, request, redirect, url_for, jsonify
from drivers.pump_v0 import Pump  # Import your Pump class
from drivers.stepper import A4988  # Import your A4988 class
from drivers.program import Program # Import your Program class
import RPi.GPIO as GPIO

app = Flask(__name__)

# Initialize stepper and pump objects globally
pin_map = {
    'DIR': {'number': 27, 'init': GPIO.LOW},
    'STEP': {'number': 26, 'init': GPIO.LOW},
    'MS3': {'number': 23, 'init': GPIO.LOW},
    'MS2': {'number': 22, 'init': GPIO.LOW},
    'MS1': {'number': 21, 'init': GPIO.LOW},
    'ENABLE': {'number': 20, 'init': GPIO.HIGH},
}
stepper = A4988(pin_mappings=pin_map, auto_calibrate=True, speed=2, pulseWidth=5E-6)
pump = Pump(stepper, syringe_volume=5, syringe_limits=(0, 10000))

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/setup', methods=['GET', 'POST'])
def setup():
    if request.method == 'POST':
        syringe_volume = request.form['syringe_volume']
        lead_screw_pitch = request.form['lead_screw_pitch']
        pump.syringe_volume = float(syringe_volume)
        pump.prompt_for_screw_data(float(lead_screw_pitch))
        return redirect(url_for('calibration'))
    return render_template('setup.html')

@app.route('/calibration', methods=['GET', 'POST'])
def calibration():
    if request.method == 'POST':
        num_points = request.form['num_points']
        pump.calibrate_volume(int(num_points))
        return redirect(url_for('program'))
    return render_template('calibration.html')

@app.route('/program', methods=['GET', 'POST'])
def program():
    if request.method == 'POST':
        commands = request.form['commands']
        program = Program(pump)
        program.parse_and_execute(commands)
        return redirect(url_for('program'))
    return render_template('program.html')

if __name__ == '__main__':
    app.run(debug=True)

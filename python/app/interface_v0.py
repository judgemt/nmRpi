from flask import Flask, render_template, request, redirect, url_for, jsonify
from pump_v0 import Pump  # Import your pump class

app = Flask(__name__)

# Initialize pump object globally (could make this session-specific later)
pump = Pump(stepper=None, syringe_volume=5, syringe_limits=(0, 10000))

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/setup', methods=['GET', 'POST'])
def setup():
    if request.method == 'POST':
        # Handle syringe volume, lead screw pitch, etc.
        syringe_volume = request.form['syringe_volume']
        lead_screw_pitch = request.form['lead_screw_pitch']
        # Call pump methods to set these parameters
        pump.syringe_volume = float(syringe_volume)
        pump.prompt_for_screw_data(float(lead_screw_pitch))
        return redirect(url_for('calibration'))
    return render_template('setup.html')

@app.route('/calibration', methods=['GET', 'POST'])
def calibration():
    if request.method == 'POST':
        # Handle calibration process
        num_points = request.form['num_points']
        pump.calibrate_volume(int(num_points))
        return redirect(url_for('program'))
    return render_template('calibration.html')

@app.route('/program', methods=['GET', 'POST'])
def program():
    if request.method == 'POST':
        # Handle user-entered program commands
        commands = request.form['commands']
        # Parse commands and execute them
        program = Program(pump)
        program.parse_and_execute(commands)
        return redirect(url_for('program'))
    return render_template('program.html')

if __name__ == '__main__':
    app.run(debug=True)

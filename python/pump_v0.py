from scipy.stats import linregress
from drivers.stepper import A4988
import RPi.GPIO as GPIO

class Pump:
    def __init__(self, stepper: A4988, syringe_volume, syringe_limits, void_volume=0):
        self.stepper = stepper  # A4988 object controlling the motor
        self.syringe_volume = syringe_volume  # Total volume of syringe in mL
        self.syringe_limits = syringe_limits  # Min and max positions (in steps)
        self.void_volume = void_volume  # Volume in lines to clear
        self.current_volume = 0  # Track current liquid in the syringe
        self.movement_history = []  # To log movements
        self.retracted = True  # Track if the syringe is retracted or pushed
        self.sample_from = None  # Source location
        self.sample_to = None  # Target location
        self.calibration_data = None  # Stores calibration results (equation and R²)

    def calibrate_volume(self):
        """Guide the user through volume calibration by collecting mass-based measurements."""
        # Step 1: Gather syringe details from the user
        syringe_volume = float(input("Enter the syringe volume in mL: "))
        syringe_length_cm = float(input("Enter the distance (in cm) between 0 mL and full marks: "))
        print(f"Estimating number of steps for full range of {syringe_volume} mL...")

        # Estimate steps for full range
        total_steps = self.stepper.motor_spr * (syringe_length_cm / syringe_volume)
        print(f"Estimated number of steps for full range: {total_steps}")

        # Set max pull volume for the syringe
        self.syringe_limits = (0, total_steps)

        # Step 2: Ask the user for the number of calibration points
        num_points = int(input("Enter the number of calibration points (minimum 3): "))
        if num_points < 3:
            raise ValueError("Calibration requires at least 3 points.")
        
        # Generate calibration points (evenly distributed across the syringe volume)
        calibration_volumes = [round(syringe_volume * i / num_points, 2) for i in range(1, num_points+1)]
        print(f"Calibration volumes: {calibration_volumes} mL")

        # Step 3: Recommend tube size for the calibration process
        total_volume_needed = sum(calibration_volumes)
        print(f"Ensure a tube of at least {total_volume_needed} mL is used.")

        # Step 4: Begin the measurement process
        masses = []
        steps_recorded = []
        input("Weigh the empty tube with a small amount of liquid and press Enter.")

        for volume in calibration_volumes:
            input(f"Position the tube for filling and press Enter to dispense {volume} mL.")
            
            # Move the syringe to dispense the volume
            steps_needed = volume * total_steps / syringe_volume
            self.stepper.move(revolutions=None, steps=steps_needed, stepMode="full", speed=1)
            
            # Prompt the user to weigh the tube with the dispensed liquid
            mass = float(input(f"Enter the total mass (in mg) after dispensing {volume} mL: "))
            masses.append(mass)
            steps_recorded.append(steps_needed)

        # Step 5: Perform linear regression on the calibration data
        print("Calculating calibration equation...")
        slope, intercept, r_value, p_value, std_err = linregress(steps_recorded, masses)
        
        # Save calibration data
        self.calibration_data = {
            "slope": slope,
            "intercept": intercept,
            "r_squared": r_value**2,
        }
        
        print(f"Calibration complete. R² = {r_value**2:.4f}")
        print(f"Calibration equation: mass (mg) = {slope:.4f} * steps + {intercept:.4f}")
        
    def move_volume(self, volume, speed):
        """Move the syringe a specific volume based on the calibration."""
        if self.calibration_data is None:
            raise RuntimeError("Pump is not calibrated. Please run calibrate_volume() first.")
        
        # Calculate steps required using the calibration equation
        slope = self.calibration_data['slope']
        intercept = self.calibration_data['intercept']
        
        # Convert volume (in mL) to mass (in mg)
        mass = volume * 1000  # Assuming water (1 mL = 1000 mg)
        steps_needed = (mass - intercept) / slope
        
        # Move the syringe based on calculated steps
        self.stepper.move(revolutions=None, steps=steps_needed, stepMode="full", speed=speed)
        
        # Log movement
        self.record_movement(volume, "push")
    
    def record_movement(self, volume, direction):
        """Record each movement into the history."""
        timestamp = time.time()
        movement = {"volume": volume, "direction": direction, "timestamp": timestamp}
        self.movement_history.append(movement)

class Pump:
    def __init__(self, motor, syringe_volume=5.0, syringe_limits=(0, 10000), ml_per_rotation=None, motor_spr=200):
        """
        Initializes the Pump class.
        
        Args:
            motor (A4988Stepper): The motor instance controlling the pump.
            syringe_volume (float): Total volume of the syringe in mL.
            syringe_limits (tuple): Tuple defining the min and max steps for the syringe.
            ml_per_rotation (float): Optional. Volume in mL per motor rotation.
            motor_spr (int): Steps per revolution for the motor.
        """
        self.motor = motor
        self.syringe_volume = syringe_volume
        self.syringe_limits = syringe_limits
        self.ml_per_rotation = ml_per_rotation  # Direct mL per rotation if provided
        self.motor_spr = motor_spr  # Steps per revolution for the motor
        self.volume_calibration = None if ml_per_rotation is None else {'ml_per_rotation': ml_per_rotation}
        self.movement_history = []
        self.retracted = False
        self.sample_from = None
        self.sample_to = None

    def move_volume(self, volume, direction="in", speed=1):
        """
        Move a specified volume in or out, depending on the direction.

        Args:
            volume (float): Volume in mL to move.
            direction (str): "in" or "out" to control the syringe's movement.
            speed (float): Speed in revolutions per second.
        """
        steps = self._volume_to_steps(volume)
        
        if steps > self.syringe_limits[1]:
            raise ValueError("Requested volume exceeds syringe limits.")
        
        # Set direction based on "in" or "out" command
        motor_direction = "CW" if direction == "in" else "CCW"
        self.motor.move(steps, stepMode="full", direction=motor_direction, speed=speed)
        
        # Record the movement
        self.record_movement(volume, direction)

    def _volume_to_steps(self, volume):
        """
        Convert a volume (mL) to steps based on ml_per_rotation or calibration.
        
        Args:
            volume (float): Volume in mL to convert to steps.
        
        Returns:
            int: Number of steps corresponding to the volume.
        """
        if self.volume_calibration:
            # If ml_per_rotation is provided, calculate steps using it
            if 'ml_per_rotation' in self.volume_calibration:
                ml_per_rotation = self.volume_calibration['ml_per_rotation']
                steps_per_ml = self.motor_spr / ml_per_rotation
            else:
                # Use steps_per_ml from calibration
                steps_per_ml = self.volume_calibration.get('steps_per_ml')
        else:
            raise RuntimeError("No calibration or ml_per_rotation provided. Please calibrate or set ml_per_rotation.")
        
        return int(volume * steps_per_ml)

    def calibrate_volume(self, points):
        """
        Guide the user through a volume calibration process if ml_per_rotation isn't provided.
        
        Args:
            points (list of tuple): List of (steps, volume) pairs for calibration.
        """
        if self.ml_per_rotation:
            print("Calibration skipped as ml_per_rotation is provided.")
            return

        print("Calibrating volume...")

        # Collect data from points and calculate steps-per-ml (linear approximation here)
        total_steps = sum(p[0] for p in points)
        total_volume = sum(p[1] for p in points)
        steps_per_ml = total_steps / total_volume
        
        # Store the calibration factor
        self.volume_calibration = {'steps_per_ml': steps_per_ml}
        print("Calibration complete: steps per mL =", steps_per_ml)

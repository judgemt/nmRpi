import time

class Pump:
    def __init__(self, motor, syringe_volume=5.0, syringe_limits=(0, 10000), ml_per_rotation=None, motor_spr=200, step_mode="full"):
        """
        Initializes the Pump class.
        
        Args:
            motor (A4988Stepper): The motor instance controlling the pump.
            syringe_volume (float): Total volume of the syringe in mL.
            syringe_limits (tuple): Tuple defining the min and max steps for the syringe.
            ml_per_rotation (float): Optional. Volume in mL per motor rotation.
            motor_spr (int): Steps per revolution for the motor.
            step_mode (str): Default step mode to use for all movements ("full", "half", etc.).
        """
        self.motor = motor
        self.syringe_volume = syringe_volume
        self.syringe_limits = syringe_limits
        self.ml_per_rotation = ml_per_rotation
        self.motor_spr = motor_spr
        self.step_mode = step_mode  # Default step mode for the pump
        self.volume_calibration = None if ml_per_rotation is None else {'ml_per_rotation': ml_per_rotation}
        self.movement_history = []
        self.retracted = False

        # Set the step mode initially
        self.set_step_mode(step_mode)

    def set_step_mode(self, step_mode):
        """Sets the step mode for all movements and updates the motor configuration."""
        self.step_mode = step_mode
        self.motor.set_step_type(step_mode)
        print(f"Step mode set to {self.step_mode} for all movements.")

    def move_volume(self, volume, speed=1):
        """
        Dispenses a specified volume. If the volume exceeds the syringe capacity,
        it will perform multiple draw-push cycles to dispense the full volume.
        
        Args:
            volume (float): Volume in mL to dispense.
            speed (float): Speed in revolutions per second.
        """
        if volume <= 0:
            raise ValueError("Volume must be greater than zero.")

        # Convert volume to revolutions using ml_per_rotation
        if self.ml_per_rotation is None:
            raise RuntimeError("ml_per_rotation must be provided for volume-to-revolutions conversion.")

        revolutions = volume / self.ml_per_rotation
        max_revolutions_per_dispense = self.syringe_volume / self.ml_per_rotation

        # Perform dispensing in cycles if the volume exceeds syringe capacity
        while revolutions > 0:
            revolutions_to_dispense = min(revolutions, max_revolutions_per_dispense)

            if not self.retracted:
                print("Drawing liquid into the syringe...")
                self._draw_syringe(revolutions=max_revolutions_per_dispense, speed=speed)
                self.retracted = True

            print(f"Pushing {revolutions_to_dispense * self.ml_per_rotation:.2f} mL out of the syringe...")
            self._push_syringe(revolutions=revolutions_to_dispense, speed=speed)
            self.retracted = False

            # Record the movement and reduce remaining revolutions
            dispensed_volume = revolutions_to_dispense * self.ml_per_rotation
            self.record_movement(dispensed_volume, "in")
            revolutions -= revolutions_to_dispense

    def _draw_syringe(self, revolutions, speed):
        """Moves the plunger to draw liquid into the syringe by a given number of revolutions."""
        self.motor.move(revolutions, stepMode=self.step_mode, direction="CCW", speed=speed)
        print(f"Drew {revolutions} revolutions (equivalent to {revolutions * self.ml_per_rotation:.2f} mL) into the syringe.")

    def _push_syringe(self, revolutions, speed):
        """Moves the plunger to push liquid out of the syringe by a given number of revolutions."""
        self.motor.move(revolutions, stepMode=self.step_mode, direction="CW", speed=speed)
        print(f"Pushed {revolutions} revolutions (equivalent to {revolutions * self.ml_per_rotation:.2f} mL) out of the syringe.")

    def record_movement(self, volume, direction):
        """Records a movement in the movement history."""
        self.movement_history.append({'volume': volume, 'direction': direction, 'timestamp': time.time()})
        print(f"Recorded movement: {volume} mL {direction}")

    def print_info(self):
        """Prints the current status and configuration of the pump."""
        print("\nPump Status and Configuration:")
        print(f"- Syringe Volume: {self.syringe_volume} mL")
        print(f"- Syringe Limits: {self.syringe_limits} steps")
        print(f"- Motor Steps per Revolution (SPR): {self.motor_spr}")
        print(f"- Volume Calibration: {self.volume_calibration}")
        print(f"- ml per Rotation: {self.ml_per_rotation if self.ml_per_rotation else 'Not provided'}")
        print(f"- Current Step Mode: {self.step_mode}")
        print(f"- Retracted State: {'Yes' if self.retracted else 'No'}")

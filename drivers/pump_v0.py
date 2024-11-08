import time

class Pump:
    def __init__(self, motor, syringe_volume=5.0, ml_per_rotation=1.0, step_mode="full"):
        """
        Initializes the Pump class.
        
        Args:
            motor (A4988Stepper): The motor instance controlling the pump.
            syringe_volume (float): Total volume of the syringe in mL.
            ml_per_rotation (float): Volume in mL per motor rotation.
            step_mode (str): Default step mode to use for all movements ("full", "half", etc.).
        """
        self.motor = motor
        self.syringe_volume = syringe_volume
        self.ml_per_rotation = ml_per_rotation
        self.step_mode = step_mode
        self.movement_history = []
        self.retracted = False  # Track syringe position (True if fully drawn, False if fully pushed)
        # self.is_disabled = True  # Track motor state

        # Set the step mode initially
        self.set_step_mode(step_mode)

    def set_step_mode(self, step_mode):
        """Sets the step mode for all movements and updates the motor configuration."""
        self.step_mode = step_mode
        self.motor.set_step_type(step_mode)
        print(f"Step mode set to {self.step_mode} for all movements.")

    # def disable(self):
    #     # NOTE: this is only provided as a convenient way to ensure the pump is disabled when necessary. 
    #     if not self.is_disabled:
    #         self.motor.disable()
    #         print("Motor disabled")
    #         self.is_disabled = True  # Only log the state change    

    def move_volume(self, volume, speed=1):
        """
        Dispenses the specified volume, handling multiple draw-push cycles if needed.

        Args:
            volume (float): Volume in mL to dispense.
            speed (float): Speed in revolutions per second.
        """
        if volume <= 0:
            raise ValueError("Volume must be greater than zero.")

        remaining_volume = volume
        max_volume_per_dispense = self.syringe_volume

        # Dispense in draw-push cycles based on volume conditions
        while remaining_volume > 0:
            if remaining_volume <= max_volume_per_dispense:
                # Single cycle if remaining volume is within syringe capacity
                volume_to_dispense = remaining_volume

            elif max_volume_per_dispense < remaining_volume <= 2 * max_volume_per_dispense:
                # Split volume into two equal cycles if between 1 and 2 syringe volumes
                volume_to_dispense = remaining_volume / 2

            else:
                # Use full syringe volume if more than 2 syringe volumes are needed
                volume_to_dispense = max_volume_per_dispense

            # Only draw the needed volume for each cycle
            if not self.retracted:
                self._draw_syringe(volume=volume_to_dispense, speed=speed)
                self.retracted = True
                time.sleep(1)

            # Push out the calculated volume in the syringe
            print(f"Pushing {volume_to_dispense:.2f} mL out of the syringe...")
            self._push_syringe(volume=volume_to_dispense, speed=speed)
            self.retracted = False  # Ensure we end in the pushed position
            time.sleep(1)

            # Record the movement and update remaining volume
            self.record_movement(volume_to_dispense, "in")
            remaining_volume -= volume_to_dispense

    def _draw_syringe(self, volume, speed):
        """Draws liquid into the syringe by converting volume to revolutions and moving the motor."""
        revolutions = volume / self.ml_per_rotation
        self.motor.move(revolutions, stepMode=self.step_mode, direction="CW", speed=speed)
        print(f"Drew {volume:.2f} mL into the syringe (equivalent to {revolutions:.2f} revolutions).")

    def _push_syringe(self, volume, speed):
        """Pushes liquid out of the syringe by converting volume to revolutions and moving the motor."""
        revolutions = volume / self.ml_per_rotation
        self.motor.move(revolutions, stepMode=self.step_mode, direction="CCW", speed=speed)
        print(f"Pushed {volume:.2f} mL out of the syringe (equivalent to {revolutions:.2f} revolutions).")

    def record_movement(self, volume, direction):
        """Records a movement in the movement history."""
        self.movement_history.append({'volume': volume, 'direction': direction, 'timestamp': time.time()})
        print(f"Recorded movement: {volume} mL {direction}")

    def print_info(self):
        """Prints the current status and configuration of the pump."""
        print("\nPump Status and Configuration:")
        print(f"- Syringe Volume: {self.syringe_volume} mL")
        print(f"- ml per Rotation: {self.ml_per_rotation}")
        print(f"- Current Step Mode: {self.step_mode}")
        print(f"- Retracted State: {'Yes' if self.retracted else 'No'}")
        print(f"- Movement History: {self.movement_history}")

import time

class Pump:
    # Class variable to track which pump is currently active
    _active_pump = None

    def __init__(self, motor, syringe_volume=5.0, ml_per_rotation=1.0, step_mode="full", max_travel_mm=100):
        """
        Initializes the Pump class.
        
        Args:
            motor (A4988): The motor instance controlling this pump
            syringe_volume (float): Total volume of the syringe in mL
            ml_per_rotation (float): Volume in mL per motor rotation
            step_mode (str): Default step mode
            max_travel_mm (float): Maximum travel distance in mm
        """
        self.motor = motor
        self.syringe_volume = syringe_volume
        self.ml_per_rotation = ml_per_rotation
        self.step_mode = step_mode
        self.max_travel_mm = max_travel_mm
        self.current_position = 0.0  # Track position as fraction of total travel
        self.movement_history = []
        self.retracted = False
        self.enabled = False
        
        # Set initial step mode
        self.set_step_mode(step_mode)

    def enable(self):
        """Enable this pump and disable all others."""
        if Pump._active_pump is not None and Pump._active_pump != self:
            print("\n----- DEACTIVATING PREVIOUS PUMP -----")
            Pump._active_pump.disable()
        
        print("\n========================================")
        print(f">>>>> ACTIVATING PUMP {id(self)} <<<<<")
        print("========================================")
        
        self.motor.enable()
        self.enabled = True
        Pump._active_pump = self
        print(f"Current position: {self.current_position:.2%} drawn")
        print("----------------------------------------\n")

    def disable(self):
        """Disable this pump."""
        self.motor.disable()
        self.enabled = False
        if Pump._active_pump == self:
            Pump._active_pump = None
        print("Pump disabled.")

    @classmethod
    def get_active_pump(cls):
        """Returns the currently active pump."""
        return cls._active_pump

    def update_position(self, revolutions, direction):
        """Update the tracked position based on movement."""
        # Calculate mm per revolution based on your hardware
        mm_per_revolution = 8  # Example value - adjust based on your setup
        movement = mm_per_revolution * revolutions
        
        if direction == "CW":
            self.current_position = min(1.0, self.current_position + (movement / self.max_travel_mm))
        else:
            self.current_position = max(0.0, self.current_position - (movement / self.max_travel_mm))
            
        # Ensure position stays within bounds
        self.current_position = max(0.0, min(1.0, self.current_position))

    def move_volume(self, volume, speed=1):
        """Modified to check if pump is active before moving."""
        if Pump._active_pump != self:
            raise RuntimeError("This pump is not currently active. Enable it first.")
        
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
        """Draws liquid into the syringe and updates position."""
        revolutions = volume / self.ml_per_rotation
        self.motor.move(revolutions, stepMode=self.step_mode, direction="CW", speed=speed)
        # Update position based on movement
        movement_fraction = volume / self.syringe_volume
        self.current_position = min(1.0, self.current_position + movement_fraction)
        print(f"Drew {volume:.2f} mL into the syringe (position: {self.current_position:.2%} drawn)")

    def _push_syringe(self, volume, speed):
        """Pushes liquid out of the syringe and updates position."""
        revolutions = volume / self.ml_per_rotation
        self.motor.move(revolutions, stepMode=self.step_mode, direction="CCW", speed=speed)
        # Update position based on movement
        movement_fraction = volume / self.syringe_volume
        self.current_position = max(0.0, self.current_position - movement_fraction)
        print(f"Pushed {volume:.2f} mL out of the syringe (position: {self.current_position:.2%} drawn)")

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

    def set_step_mode(self, step_mode):
        """Sets the step mode for all movements and updates the motor configuration."""
        self.step_mode = step_mode
        self.motor.set_step_type(step_mode)
        print(f"Step mode set to {self.step_mode} for all movements.")

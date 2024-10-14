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
        self.lead_screw_pitch = None  # Pitch of the screw (distance moved per revolution in mm)

    def prompt_for_screw_data(self):
        """Prompt the user for lead screw data or help them measure it."""
        # Step 1: Ask if the user knows the screw pitch
        knows_pitch = input("Do you know the lead screw pitch (distance moved per revolution) in mm? (y/n): ").lower()

        if knows_pitch == 'y':
            self.lead_screw_pitch = float(input("Enter the lead screw pitch (in mm): "))
        else:
            # Step 2: Guide the user through a manual measurement
            print("Let's measure the lead screw pitch manually.")
            input("Ensure the syringe is fully retracted and press Enter to continue...")
            
            # Move the screw by a known number of revolutions (e.g., 5 full revolutions)
            revolutions = 5
            print(f"Moving the screw by {revolutions} full revolutions.")
            self.stepper.move(revolutions=revolutions, stepMode="full", speed=1, direction="CW")
            
            # Prompt the user to measure the distance moved
            distance_moved = float(input("Measure the distance the syringe moved (in mm) and enter the value: "))
            
            # Calculate the screw pitch based on revolutions and distance
            self.lead_screw_pitch = distance_moved / revolutions
            print(f"Estimated lead screw pitch: {self.lead_screw_pitch:.3f} mm per revolution.")
        
        return self.lead_screw_pitch

    def calculate_revolutions_for_syringe(self):
        """Estimate the number of revolutions for the syringe's full range based on pitch."""
        if self.lead_screw_pitch is None:
            print("Lead screw pitch is not set. Please run the prompt_for_screw_data() first.")
            return

        # Step 3: Ask the user for the syringe length (distance between min and max marks in mm)
        syringe_length = float(input("Enter the length of the syringe's travel (distance between the bottom and top marks in mm): "))
        
        # Calculate the number of revolutions for the full syringe range
        total_revolutions = syringe_length / self.lead_screw_pitch
        print(f"Estimated number of revolutions for the full range of the syringe: {total_revolutions:.2f}")
        
        return total_revolutions

# # Example of how it might be used:

# # Initialize the Pump object
# stepper = A4988(pin_mappings=pin_map, auto_calibrate=True, speed=2, pulseWidth=5E-6)
# pump = Pump(stepper, syringe_volume=5, syringe_limits=(0, 10000))

# # Prompt the user for lead screw data
# pitch = pump.prompt_for_screw_data()

# # Estimate revolutions for full syringe motion
# revolutions = pump.calculate_revolutions_for_syringe()

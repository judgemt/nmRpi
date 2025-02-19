from drivers.methods.a4988 import *
from drivers.utils import Microstep


class A4988:
    """Handles all A4988 drivers as a cluster to ensure only one is activated at a time."""
    def __init__(self, config_file='config/pin_map.json',enable_pins=None,speed=50,motor_spr=200):
        enable_pins = [21,19]
            
        # Setup driver info

        self.pins_shared = load_pin_configurations(config_file)
        self.pins_enable = enable_pins
        self.relative_position = [0]*len(self.pins_enable) # in full steps
        self.steps_per_rotation = motor_spr
        self.steps_per_second = speed
        self.direction = 'Counterclockwise'

        # Setup pins
        self.pi = setup_pigpio()
        setup_shared_pins(self.pins_shared, self.pi)
        setup_enable_pins(self.pins_enable)
        self.microstep = Microstep(self.pins_shared, mode='sixteenth')
 
        # Perform checks
        
    def set_speed(self, new_speed):
        # Check if new_speed is valid
        
        # Print log of old and new speed

        # Set new speed
        self.steps_per_second = new_speed
    

    def get_speed(self):
        return(self.steps_per_second)

    def set_direction(self, direction):
        pins = self.pins_shared
        if direction == "Clockwise":
            GPIO.output(pins['DIR']['number'], GPIO.LOW)
            self.direction = direction
            print('Direction set to "Clockwise"')
        elif direction == "Counterclockwise":
            GPIO.output(pins['DIR']['number'], GPIO.HIGH)
            self.direction = direction
            print('Direction set to "Counterclockwise"')
        else:
            RuntimeError(f'Direction "{direction}" should be "Clockwise" or "Counterclockwise".')

    def get_direction(self):
        return self.direction
    
    def to_steps_per_second(rotations_per_second, steps_per_rotation):
        return steps_per_rotation * rotations_per_second

    def set_step_mode(self, step_mode='sixteenth'):
        self.microstep.set_mode(step_mode)

    def update_position(self, driver_number=None, steps=None):
        """Update relative position of a specific driver."""
        # Ensure driver_number is valid
        if driver_number is None or driver_number < 0 or driver_number >= len(self.relative_position):
            raise ValueError(f"Invalid driver_number: {driver_number}")

        # Ensure steps is a valid integer
        if steps is None or not isinstance(steps, (int, float)):
            raise ValueError(f"Invalid steps value: {steps}")

        direction = self.get_direction()

        if direction == "Clockwise":
            self.relative_position[driver_number] -= steps
        elif direction == "Counterclockwise":
            self.relative_position[driver_number] += steps
        else:
            raise RuntimeError("Cannot update position if direction is not defined.")

    def get_position(self, driver_number):
        """Retrieve relative position for a specific driver."""
        if driver_number is None or driver_number < 0 or driver_number >= len(self.relative_position):
            raise ValueError(f"Invalid driver_number: {driver_number}")

        return self.relative_position[driver_number]

    def is_enabled(self):
        pass

    def enable(self, driver_number):
        enable(self.pins_enable, driver_number)

    def disable_all(self):
        disable(self.pins_enable)

   ## Running ############################

    def move(self, driver_number=None, direction='Counterclockwise', n_steps=None, 
            steps_per_second=50, step_mode='sixteenth'):

        if driver_number not in range(len(self.pins_enable)):
            self.disable_all()
            raise RuntimeError('A4988.move: enable pin index must be provided. Drivers disabled; skipping move command.')

        if n_steps is None or not isinstance(n_steps, (int, float)):
            raise ValueError("A4988.move: n_steps must be provided and must be a number.")

        print('\n------------------------------')
        print(f'Driver {driver_number}:')
        print(f'Position before move: {self.get_position(driver_number)}')

        try:
            self.set_direction(direction)   
            self.enable(driver_number)

            pulse_step(
                self.pi,
                self.pins_shared['STEP']['number'],  # Uses board numbering
                n_steps=n_steps, 
                microseconds_high=10,
                steps_per_second=steps_per_second,
                microstep_factor=self.microstep.get_factor()
            )
            
            time.sleep(1)

            # ✅ Update position BEFORE disabling the driver
            self.update_position(driver_number, n_steps)

            self.disable_all()
            print(f'Position after move: {self.get_position(driver_number)}')
            print('------------------------------')

        except Exception as e:
            print(f"Error: {e}")
            self.disable_all()
            print('Driver inactive')

    def shutdown(self):
        self.disable_all()
        cleanup_pins(self.pi)
        print("All drivers inactivated")
        shutdown_pigpio()
        

from methods.a4988 import *
from utils import Microstep


class A4988:
    """Handles all A4988 drivers as a cluster to ensure only one is activated at a time."""
    def __init__(self, config_file='config/pin_map.json',enable_pins=None,speed=50,motor_spr=200):
        enable_pins = [21,19]
        steps_per_second = 200
        steps_per_rotation = 200
            
        # Setup driver info

        self.pins_shared = load_pin_configurations(config_file)
        self.pins_enable = enable_pins
        self.relative_position = 0 # in full steps
        self.steps_per_rotation = motor_spr
        self.steps_per_second = speed

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
        pass

    def get_speed(self):
        return(self.steps_per_second)

    def set_direction(self, direction):
        if direction is "Clockwise":
            pins = self.pins_shared
            GPIO.output(pins['DIR']['number'], GPIO.LOW)
            print('Direction set to "Clockwise"')
        elif direction is "Counterclockwise":
            GPIO.output(pins['DIR']['number'], GPIO.HIGH)
            print('Direction set to "Counterclockwise"')
        else:
            RuntimeError(f'Direction "{direction}" should be "Clockwise" or "Counterclockwise".')

    def to_steps_per_second(rotations_per_second, steps_per_rotation):
        return steps_per_rotation * rotations_per_second

    def set_step_mode(self, step_mode='sixteenth'):
        self.microstep.set_mode(step_mode)

    def update_position(self, steps, direction):
        if direction == "Clockwise":
            self.relative_position -= steps
        elif direction == "Counterclockwise":
            self.relative_position += steps
        else:
            raise RuntimeError('Cannot update position if direction is not define.')

    def get_position(self):
        pass

    def is_enabled(self):
        pass

    def enable(self, pin):
        gpio.enable(self.pins_enable, pin)

   ## Running ############################

    def move(self, direction='Counterclockwise', n_steps=None, 
             steps_per_second=50,step_mode='sixteenth'):
        
        try: 
            self.set_direction(self,'Counterclockwise')   

            self.enable(enable_pins, 0)
            pulse_step(pi,
                        pins['STEP']['number'], # this uses board numbering
                        n_steps=n_steps, 
                        microseconds_high=10,
                        steps_per_second=steps_per_second,
                        microstep_factor = microstep.get_factor()) 
            
            time.sleep(1)

            set_direction('Clockwise')   
            pulse_step(pi,
                        pins['STEP']['number'], # this uses board numbering
                        n_steps=n_steps*microstep.get_factor(), 
                        microseconds_high=10,
                        steps_per_second=steps_per_second*microstep.get_factor())


            set_direction('Counterclockwise')   
            enable(enable_pins, 1)
            pulse_step(pi,
                        pins['STEP']['number'], # this uses board numbering
                        n_steps=n_steps*microstep.get_factor(), 
                        microseconds_high=10,
                        steps_per_second=steps_per_second*microstep.get_factor()) 
            
            time.sleep(1)

            set_direction('Clockwise')   
            pulse_step(pi,
                        pins['STEP']['number'], # this uses board numbering
                        n_steps=n_steps*microstep.get_factor(), 
                        microseconds_high=10,
                        steps_per_second=steps_per_second*microstep.get_factor())

            disable_all(enable_pins)
            print('steps complete')

        except Exception as e:
            print(f"Error: {e}")
            cleanup_pins(pi)
            print('Driver inactive')
            exit(1)

    cleanup_pins(pi)
    print('Driver inactive')
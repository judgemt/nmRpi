from methods.a4988 import *
from utils import Microstep

class A4988:

    def __init__(self, config_file='config/pin_map.json',enable_pins=None,speed=50,motor_spr=200):
        pass

    def set_direction(direction):
        if direction is "Clockwise":
            GPIO.output(pins['DIR']['number'], GPIO.LOW)
            print('Direction set to "Clockwise"')
        elif direction is "Counterclockwise":
            GPIO.output(pins['DIR']['number'], GPIO.HIGH)
            print('Direction set to "Counterclockwise"')
        else:
            RuntimeError(f'Direction "{direction}" should be "Clockwise" or "Counterclockwise".')

    def to_steps_per_second(rotations_per_second, steps_per_rotation):
        return steps_per_rotation * rotations_per_second

    def set_step_mode():
        pass

    def update_position():
        pass

    def get_position():
        pass

    def is_enabled():
        pass

    ## Setup ##############################

    enable_pins = [21,19]
    steps_per_second = 200
    steps_per_rotation = 200
    n_steps = 200

    def initialize_driver(enable_pins):
        pins = load_pin_configurations()
        pi = setup_pigpio()    
        setup_gpio()
        setup_enable_pins(enable_pins)
        setup_pins(pins, pi)
        microstep = Microstep(pins, mode = 'sixteenth')

    
    ## Running ############################

    def move(direction='Counterclockwise', n_steps=None, 
             steps_per_second=50,step_mode='sixteenth'):
        try: 
            set_direction('Counterclockwise')   

            enable(enable_pins, 0)
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
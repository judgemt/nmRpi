import pygame as pg
from drivers.driver import A4988

driver_numbers = [0,1]
driver = A4988(config_file='./config/pin_map.json',enable_pins=[19,21])

active_driver = None
direction = None

pg.init()
screen = pg.display.set_mode((400,300))

running = True
while running:
    for event in pg.event.get():

        if event.type == pg.KEYDOWN:
            # A key has been pressed. 
            key = event.key

            # First, see if it's an integer:
            if pg.K_0 <= key <= pg.K_9:
                key = key - pg.K_0

                if key in driver_numbers:
                    active_driver = key

            # If not an integer, assume it's a char or arrow:
            else:
                # If key is arrow, set direction
                if key == pg.K_RIGHT: # draw
                    direction = 'Counterclockwise'
                    print(f"Direction: {direction}")
                elif key == pg.K_LEFT: # push
                    direction = 'Clockwise'
                    print(f"Direction: {direction}")
                elif key == pg.K_q: # exit
                    print("quitting")
                    active_driver = direction = None
                    running = False
                else: 
                    print('key stroke not recognized')

                # If a driver is active and direction is set, do a movement:
                if active_driver is not None and direction is not None:
                    driver.move(driver_number=active_driver, direction=direction, n_steps=100, steps_per_second=200)
                    print(f"Driver {active_driver} moved {direction}")
                    
                else:
                    print("Nothing happened")
       
print('Driver inactive')
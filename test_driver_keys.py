from drivers.driver import A4988
import keyboard as kb

driver_numbers = [0,1]
driver = A4988(config_file='./config/pin_map.json',enable_pins=[19,21])
active_driver = None

while True:
    key_event = kb.read_event()

    if key_event.event_type == kb.KEY_DOWN:
        try:
            response = int(key_event.name)

            if key_event.name in driver_numbers:
                active_driver == key_event

        except:
            response = key_event.name

            # If response is arrow, interpret as draw (right) or push (left)
            if response == 'right': # draw
                direction = 'Counterclockwise'
            elif response == 'left': # push
                direction = 'Clockwise'
            else: 
                print('key stroke not recognized')

            # Actually do the movement:
            if active_driver is not None and direction is not None:
                driver.move(driver_number=active_driver, direction=direction, n_steps=200, steps_per_second=50)
                response = direction = None # reset so we don't run again

        except KeyboardInterrupt:
            driver.disable_all()
            break
print('Driver inactive')
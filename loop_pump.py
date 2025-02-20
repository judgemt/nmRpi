from drivers.driver import A4988
import time

driver = A4988(config_file='./config/pin_map.json',enable_pins=[19,21])


speed = 150
target_steps_per_iteration = 100

uL_desired = 5e3
ul_per_step = 0.5
steps = uL_desired / ul_per_step
iterations = steps / target_steps_per_iteration

print('Initial draw-push to clear air...')
driver.move(driver_number=1, direction='Counterclockwise', n_steps=300, steps_per_second=speed)
time.sleep(1)
driver.move(driver_number=1, direction='Clockwise', n_steps=300, steps_per_second=speed)
time.sleep(1)
 
for i in range(iterations):

    print(f'Iteration {i}')

    try:
        print('draw 100 steps...')
        driver.move(driver_number=1, direction='Counterclockwise', n_steps=steps_per_iteration, steps_per_second=speed)
        time.sleep(1)
        print('push 100 steps...')
        driver.move(driver_number=1, direction='Clockwise', n_steps=steps_per_iteration, steps_per_second=speed)
        time.sleep(1)

    except:
        driver.shutdown()
        break

driver.shutdown()
print('Driver inactive')

volume_est = steps * ul_per_step * iterations
print('Volume estimated: ')
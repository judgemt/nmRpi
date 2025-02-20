from drivers.driver import A4988
import time

driver = A4988(config_file='./config/pin_map.json',enable_pins=[19,21])

print('Initial draw...')
driver.move(driver_number=1, direction='Counterclockwise', n_steps=300, steps_per_second=100)
time.sleep(1)

for i in range(10):

    print(f'Iteration {i}')

    try:
        print('draw 100 steps...')
        driver.move(driver_number=1, direction='Counterclockwise', n_steps=100, steps_per_second=100)
        time.sleep(1)
        print('push 100 steps...')
        driver.move(driver_number=1, direction='Clockwise', n_steps=100, steps_per_second=20)
        print(f'Sample @ {i*0.5} mL')
        print(f'DSS/D2O @ {i*50} uL')

    except:
        driver.shutdown()
        break

driver.shutdown()
print('Driver inactive')
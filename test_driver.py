from drivers.driver import A4988
driver = A4988(config_file='./config/pin_map.json',enable_pins=[19,21])

driver.move(driver_number=0, direction='Counterclockwise', n_steps=50, steps_per_second=50)

print('Driver inactive')
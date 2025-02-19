from drivers.driver import A4988
driver = A4988(config_file='./config/pin_map.json',enable_pins=[19,21])
driver.move(driver_number=1, direction='Counterclockwise', n_steps=200, steps_per_second=50)
driver.move(driver_number=1, direction='Clockwise', n_steps=200, steps_per_second=50)
# while True:
#     try:
#         # driver.move(driver_number=0, direction='Counterclockwise', n_steps=50, steps_per_second=50)
#         driver.move(driver_number=1, direction='Counterclockwise', n_steps=200, steps_per_second=50)
#         # driver.move(driver_number=0, direction='Clockwise', n_steps=150, steps_per_second=50)
#         driver.move(driver_number=1, direction='Clockwise', n_steps=200, steps_per_second=50)
#     except KeyboardInterrupt:
#         driver.disable_all()
#         break
driver.disable_all()
print('Driver inactive')
import pygame as pg
from drivers.driver import A4988

# Initialize driver
driver_numbers = [0, 1]
driver = A4988(config_file='./config/pin_map.json', enable_pins=[19, 21], speed=50)

# Initial motor settings
active_driver = None
direction = None
steps_per_second = 5
draw_speed = 20
push_speed = 10
steps = 1

# Pygame setup
pg.init()
screen = pg.display.set_mode((400, 300))
pg.display.set_caption('Welcome')

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)

# Font
font = pg.font.Font(None, 40)

# Input box
input_box = pg.Rect(100, 120, 200, 50)
text = ""
input_active = False

# Button for triggering step input
button_rect = pg.Rect(150, 200, 100, 40)
button_color = GRAY

running = True
while running:
    screen.fill(WHITE)  # Clear screen
    
    # Draw button
    pg.draw.rect(screen, button_color, button_rect)
    button_text = font.render("Set Steps", True, BLACK)
    screen.blit(button_text, (button_rect.x + 10, button_rect.y + 5))

    # Draw input box if active
    if input_active:
        pg.draw.rect(screen, BLACK, input_box, 2)
        input_surface = font.render(text, True, BLACK)
        screen.blit(input_surface, (input_box.x + 10, input_box.y + 10))

    pg.display.flip()  # Update display

    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False  # Exit

        # Detect key press
        elif event.type == pg.KEYDOWN:
            key = event.key

            # Trigger step input with 's'
            if key == pg.K_s:
                input_active = True
                text = ""

            # Handle number inputs
            elif pg.K_0 <= key <= pg.K_9:
                key_number = key - pg.K_0
                if input_active:
                    text += str(key_number)  # Collect digits for step input
                elif key_number in driver_numbers:
                    active_driver = key_number  # Select driver
            
            # Handle backspace
            elif key == pg.K_BACKSPACE and input_active:
                text = text[:-1]

            # Submit step input with Enter
            elif key == pg.K_RETURN and input_active:
                if text.isdigit():
                    steps = int(text)
                    print(f"Steps set to: {steps}")
                input_active = False  # Close input box
            
            # Handle movement keys
            elif not input_active:
                if key == pg.K_RIGHT:  # Draw
                    direction = 'Counterclockwise'
                    steps_per_second = draw_speed
                    print(f"Direction: {direction}, {steps_per_second} steps/sec")
                elif key == pg.K_LEFT:  # Push
                    direction = 'Clockwise'
                    steps_per_second = push_speed
                    print(f"Direction: {direction}, {steps_per_second} steps/sec")
                elif key == pg.K_q:  # Quit
                    print("Quitting")
                    active_driver = direction = None
                    running = False

                # Move the motor if conditions are met
                if active_driver is not None and direction is not None:
                    driver.move(driver_number=active_driver, direction=direction, n_steps=steps, steps_per_second=steps_per_second)
                    print(f"Driver {active_driver} moved {direction} for {steps} steps")
                else:
                    print("Nothing happened")

        # Detect mouse clicks
        elif event.type == pg.MOUSEBUTTONDOWN:
            if button_rect.collidepoint(event.pos):  # If button is clicked
                input_active = True
                text = ""

print('Driver inactive')
pg.quit()

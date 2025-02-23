import pygame as pg
from drivers.driver import A4988

# Initialize driver
driver_numbers = [0, 1]  # Available drivers
driver = A4988(config_file='./config/pin_map.json', enable_pins=[19, 21], speed=50)

# Initial motor settings
active_driver = None
direction = None
steps = 1
steps_per_second = 5  # Default speed
draw_speed = 20
push_speed = 10

# Pygame setup
pg.init()
screen = pg.display.set_mode((400, 400))  # Increased height for better spacing
pg.display.set_caption('Motor Control')

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)

# Font
font = pg.font.Font(None, 30)

# Define spacing
label_offset = 20  # Extra space between labels and input boxes
box_height = 40  # Standard height for input boxes
vertical_spacing = 60  # Space between input fields

# Input field positions
driver_box = pg.Rect(200, 40, 100, box_height)  # Driver input box
steps_box = pg.Rect(200, 40 + vertical_spacing, 100, box_height)  # Steps input box
speed_box_draw = pg.Rect(200, 40 + 2 * vertical_spacing, 100, box_height)  # Draw Speed input box
speed_box_push = pg.Rect(200, 40 + 3 * vertical_spacing, 100, box_height)  # Push Speed input box
update_button = pg.Rect(125, 40 + 4 * vertical_spacing, 150, 50)  # Update button

# Input states
active_input = None  # Tracks which input field is active
driver_text = ""  # Empty by default (user must enter 0 or 1)
steps_text = str(steps)  # Default step count
push_speed_text = str(push_speed)  # Default push speed
draw_speed_text = str(draw_speed)  # Default draw speed

running = True
while running:
    screen.fill(WHITE)  # Clear screen

    # Labels
    screen.blit(font.render("Driver (0/1):", True, BLACK), (50, driver_box.y + label_offset))
    screen.blit(font.render("Steps:", True, BLACK), (50, steps_box.y + label_offset))
    screen.blit(font.render("Draw Speed:", True, BLACK), (50, speed_box_draw.y + label_offset))
    screen.blit(font.render("Push Speed:", True, BLACK), (50, speed_box_push.y + label_offset))
    screen.blit(font.render(f"Active Driver: {active_driver if active_driver is not None else 'None'}", True, BLACK), (50, 360))

    # Draw input boxes
    pg.draw.rect(screen, BLACK if active_input == "driver" else GRAY, driver_box, 2)
    pg.draw.rect(screen, BLACK if active_input == "steps" else GRAY, steps_box, 2)
    pg.draw.rect(screen, BLACK if active_input == "draw speed" else GRAY, speed_box_draw, 2)
    pg.draw.rect(screen, BLACK if active_input == "push speed" else GRAY, speed_box_push, 2)

    # Render text inside input boxes
    screen.blit(font.render(driver_text, True, BLACK), (driver_box.x + 10, driver_box.y + 10))
    screen.blit(font.render(steps_text, True, BLACK), (steps_box.x + 10, steps_box.y + 10))
    screen.blit(font.render(draw_speed_text, True, BLACK), (speed_box_draw.x + 10, speed_box_draw.y + 10))
    screen.blit(font.render(push_speed_text, True, BLACK), (speed_box_push.x + 10, speed_box_push.y + 10))

    # Draw update button
    pg.draw.rect(screen, GRAY, update_button)
    screen.blit(font.render("Update", True, BLACK), (update_button.x + 40, update_button.y + 10))

    pg.display.flip()  # Update display

    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False  # Exit loop

        # Handle mouse clicks
        elif event.type == pg.MOUSEBUTTONDOWN:
            if driver_box.collidepoint(event.pos):
                active_input = "driver"
            elif steps_box.collidepoint(event.pos):
                active_input = "steps"
            elif speed_box_draw.collidepoint(event.pos):
                active_input = "draw speed"
            elif speed_box_push.collidepoint(event.pos):
                active_input = "push speed"
            elif update_button.collidepoint(event.pos):  # If update button clicked
                # Validate and update values
                if driver_text.isdigit() and int(driver_text) in driver_numbers:
                    active_driver = int(driver_text)
                else:
                    print(f"⚠ Warning: Invalid driver number {driver_text}. Select 0 or 1.")

                steps = int(steps_text) if steps_text.isdigit() else steps
                draw_speed = int(draw_speed_text) if draw_speed_text.isdigit() else draw_speed
                push_speed = int(push_speed_text) if push_speed_text.isdigit() else push_speed

                print(f"Updated values - Driver: {active_driver}, Steps: {steps}, Draw Speed: {draw_speed}, Push Speed: {push_speed}")

                # Reset active input to avoid accidental modifications
                active_input = None  

        # Handle keyboard input
        elif event.type == pg.KEYDOWN:
            if active_input:
                if event.key == pg.K_BACKSPACE:  # Remove last character
                    if active_input == "driver":
                        driver_text = driver_text[:-1]
                    elif active_input == "steps":
                        steps_text = steps_text[:-1]
                    elif active_input == "draw speed":
                        draw_speed_text = draw_speed_text[:-1]                    
                    elif active_input == "push speed":
                        push_speed_text = push_speed_text[:-1]
                elif event.unicode.isdigit():  # Append digit
                    if active_input == "driver":
                        driver_text += event.unicode
                    elif active_input == "steps":
                        steps_text += event.unicode
                    elif active_input == "draw speed":
                        draw_speed_text += event.unicode
                    elif active_input == "push speed":
                        push_speed_text += event.unicode

            # Handle movement keys
            elif event.key == pg.K_RIGHT:  # Draw
                direction = 'Counterclockwise'
                steps_per_second = draw_speed
                if active_driver is not None:
                    print(f"Moving Driver {active_driver} {direction} for {steps} steps at {steps_per_second} steps/sec")
                    driver.move(driver_number=active_driver, direction=direction, n_steps=steps, steps_per_second=steps_per_second)
                else:
                    print("⚠ Warning: No driver selected. Please enter 0 or 1 and press Update.")

            elif event.key == pg.K_LEFT:  # Push
                direction = 'Clockwise'
                steps_per_second = push_speed
                if active_driver is not None:
                    print(f"Moving Driver {active_driver} {direction} for {steps} steps at {steps_per_second} steps/sec")
                    driver.move(driver_number=active_driver, direction=direction, n_steps=steps, steps_per_second=steps_per_second)
                else:
                    print("⚠ Warning: No driver selected. Please enter 0 or 1 and press Update.")

            elif event.key == pg.K_q:  # Quit
                print("Quitting")
                running = False

print("Shutting down driver...")
driver.shutdown()
pg.quit()

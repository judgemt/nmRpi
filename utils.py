import time
import RPi.GPIO as GPIO

def calibrate_step_delay(spr, speed, pulseWidth, n):
    """Calibrate the step delay, accounting for sleep overhead and pulse width."""
    
    # Calculate steps per second (SPS)
    sps = spr * speed
    start_time = time.time()

    # Measure sleep overhead
    print('Measuring sleep overhead...')
    t1 = time.time()
    for i in range(int(n)):
        time.sleep(0)  # Perform a large number of short sleep calls to measure overhead
        time.sleep(0)  # Perform a large number of short sleep calls to measure overhead
    t2 = time.time()
    
    sleep_overhead = (t2 - t1) / n  # Average sleep overhead per step
    print(f'{n} sleeps took {t2 - t1:.6f} seconds.')
    print(f'sleep_overhead =~ {sleep_overhead:.6f} seconds per step.')
    
    # Desired step time based on speed (revs per second)
    step_desired = 1 / sps
    print(f'Desired step time = {step_desired:.6f} s.')

    # Calculate the stepDelay based on desired step time, sleep overhead, and pulse width
    stepDelay = step_desired - sleep_overhead - pulseWidth
    stepDelay = round(stepDelay, 6)

    # Ensure step delay + pulse width is not below the threshold (5 µs)
    if (stepDelay + pulseWidth) < pulseWidth:
        print(f'Step duration (stepDelay + pulseWidth) must be >= pulseWidth. Current step duration is {stepDelay + pulseWidth:.6f}.')
        stepDelay = pulseWidth
        print(f"Step delay adjusted to {stepDelay:.6f} s to meet the minimum requirement.")
    else:
        print(f'Step delay adjusted to {stepDelay:.6f} seconds to account for sleep overhead.')

    return stepDelay

# Example usage:
# ms = Microstep(pin_mapping)
# speed = 1  # Example speed (revolutions per second)
# pulseWidth = 5E-6  # Example pulse width
# step_delay = calibrate_step_delay(ms, speed, pulseWidth)

def step(n, pin, pulseWidth, stepDelay):

    start_time = time.time()

    for i in range(n):# 1 revolution
        GPIO.output(pin['STEP']['number'], GPIO.HIGH)
        time.sleep(pulseWidth)  # minimum pulse width # each of these calls costs 0.000125 s on average on an RPI4, mainly due to time.sleep overhead. Subtract this from the pulseWidth before using?
        GPIO.output(pin['STEP']['number'], GPIO.LOW)
        time.sleep(stepDelay)  # Short sleep to reduce CPU usage
    
    end_time = time.time()
    
    time_elapsed = end_time-start_time
    
    return time_elapsed
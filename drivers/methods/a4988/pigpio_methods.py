import pigpio
import subprocess
import time
import functools

def setup_pigpio():
    # Stop any running pigpio daemon
    subprocess.run(["sudo", "killall", "pigpiod"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(0.5)  # Wait before restarting

    # pigpio daemon startup (or restart)
    subprocess.run(["sudo","pigpiod"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) # start daemon
    time.sleep(1) # wait to give daemon a chance to start
    pi = pigpio.pi() # connect to daemon

    if not pi.connected:
        print('Failed to connect to pigpio daemon')
        exit(1)
    else:
        print('pigpio daemon started')
    
    return pi
    
def require_valid_pi(func):
    """Decorator to ensure pigpio instance is valid and connected."""
    @functools.wraps(func)
    def wrapper(pi, *args, **kwargs):
        if not pi.connected:
            raise RuntimeError(f"Error: Pigpio instance is not connected. Try 'sudo system status pigpiod' in Terminal.")
        return func(pi, *args, **kwargs)
    return wrapper

def BCM_number(board_pin):
    bcmnum = {
        3: 2,  5: 3,  7: 4,  8: 14,  10: 15,
        11: 17, 12: 18, 13: 27, 15: 22, 16: 23,
        18: 24, 19: 10, 21: 9,  22: 25, 23: 11,
        24: 8,  26: 7,  29: 5,  31: 6,  32: 12,
        33: 13, 35: 19, 36: 16, 37: 26, 38: 20,
        40: 21
    }
    return bcmnum[board_pin]

def generate_pulses(step_pin_board: int, n: int, microseconds_high: int, microseconds_low: int) -> list:
    """
    Generates a list of pigpio.pulse objects for stepping.

    Args:
        step_pin_board (int): BOARD pin number for the step signal.
        n_steps (int): Number of pulses to generate.
        microseconds_high (int): Time (µs) for HIGH pulse.
        microseconds_low (int): Time (µs) for LOW pulse.

    Returns:
        list: A list of pigpio.pulse objects.
    """

    if n <= 0:
        raise ValueError("n must be greater than 0.")
    


    step_pin_bcm = BCM_number(step_pin_board)
    # print(f"Generating {n} pulses on BCM {step_pin_bcm} | HIGH: {microseconds_high} µs | LOW: {microseconds_low} µs")
    # print(f'microsteps: {n}')
    pulses = []
    for step in range(n):
        pulses.append(pigpio.pulse(1 << step_pin_bcm, 0, int(microseconds_high))) # HIGH
        pulses.append(pigpio.pulse(0, 1 << step_pin_bcm, int(microseconds_low)))   # LOW

    return pulses

@require_valid_pi
def pulse_step(pi: pigpio.pi, step_pin_board: int, n_steps: int, microseconds_high: int = 10, microseconds_low: int = 10, steps_per_second=50, microstep_factor=1, batch_size=50):
    """
    Sends a sequence of pulses to step a motor using pigpio.

    Args:
        pi (pigpio.pi): Pigpio instance.
        step_pin_board (int): BOARD pin number for stepping.
        n_steps (int): Number of pulses to generate.
        microseconds_high (int, optional): Time (µs) for HIGH pulse. Default is 10.
        microseconds_low (int, optional): Time (µs) for LOW pulse. Default is 10.

    Raises:
        ValueError: If `n_steps` is <= 0.
    """
    pi.exceptions = True
    pi.wave_clear()
    time.sleep(0.1)

    # Ensure valid step count
    if n_steps <= 0:
        raise ValueError("n_steps must be greater than 0.")

    # Round n_steps to the nearest microstep increment
    rounded_steps = round(n_steps * microstep_factor) / microstep_factor
    microsteps = int(rounded_steps * microstep_factor)  # Convert back to integer count

    # Compute timing
    print(f'full steps per second: {steps_per_second}')
    step_period = 1/steps_per_second # seconds/full step
    # print(f's per step: {step_period}')
    step_period_us = step_period * 1e6  # microseconds per step
    # print(f'us per step = {step_period_us}')
    microstep_period_us = step_period_us / microstep_factor
    # print(f'microseconds per microstep (1/16th step): {microstep_period_us}')
    microseconds_low = max(10, microstep_period_us - microseconds_high)  #

    remaining_steps = microsteps
    wave_ids = []

    while remaining_steps > 0:

        batch = min(batch_size, remaining_steps)
        pulses = generate_pulses(step_pin_board, batch, microseconds_high, microseconds_low)

        if not pulses:
            raise RuntimeError("Failed to create pulses.")
    
        pi.wave_clear()               # Clear existing waveforms
        pi.wave_add_generic(pulses)   # Add new waveform
        wave_id = pi.wave_create()    # Create waveform

        if wave_id < 0:
            raise RuntimeError("Failed to create waveform.")

        wave_ids.append(wave_id)
        remaining_steps -= batch

    # print(f"Chaining {len(wave_ids)} waveforms together")
    # print(f"Sending...")
    start_time = time.time()
    # pi.wave_send_once(wave_ids[0])
    pi.wave_chain([255,0] + wave_ids)

    while pi.wave_tx_busy():      # Wait for transmission to complete
        time.sleep(0.001)

    pi.wave_clear()               # Cleanup waveforms
    end_time = time.time()
    time_elapsed = end_time - start_time
    print(f'elapsed time: {time_elapsed}')
    print(f'Target speed: {steps_per_second} steps/second')
    print(f'Effective speed: {microsteps/microstep_factor/time_elapsed} steps/second')

@require_valid_pi
def setup_pigpio_pin(pi: pigpio.pi, pin, pin_name):
    try:
        if pin_name == "STEP":
            step_pin = BCM_number(pin['number']) # pigpio assumes BCM numbering
            print('Setting STEP pin on BCM pin ',step_pin,' up with pigpio')
            pi.set_mode(step_pin, pigpio.OUTPUT)
            # print('mode set..')
            pi.set_pull_up_down(step_pin, pigpio.PUD_DOWN)
            # print('pulldown set..')
            print('STEP pin was set with internal pulldown.')

    except: 
        print(f'{pin_name} failed setup')

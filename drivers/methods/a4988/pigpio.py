import pigpio
import subprocess
import time

def setup_pigpio():
    # pigpio setup
    subprocess.run(["sudo","pigpiod"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) # start daemon
    time.sleep(1) # wait to give daemon a chance to start
    pi = pigpio.pi() # connect to daemon

    if not pi.connected:
        print('Failed to connect to pigpio daemon')
        exit(1)
    else:
        print('pigpio daemon started')
    
    return pi
    
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
    # print(f'microsteps: {n}')
    pulses = []
    for step in range(n):
        pulses.append(pigpio.pulse(1 << step_pin_bcm, 0, int(microseconds_high))) # HIGH
        pulses.append(pigpio.pulse(0, 1 << step_pin_bcm, int(microseconds_low)))   # LOW

    return pulses

def pulse_step(pi: pigpio.pi, step_pin_board: int, n_steps: int, microseconds_high: int = 10, microseconds_low: int = 10, steps_per_second=50, microstep_factor=1, batch_size=100):
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

    microseconds_low = (1/(steps_per_second*microstep_factor))*1e6 - microseconds_high
    print(f'µs low: {microseconds_low}')
    print(f'microsteps: {n_steps*microstep_factor}')

    remaining_steps = n_steps*microstep_factor
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

    print(f"Chaining {len(wave_ids)} waveforms together")
    pi.wave_chain([255,0] + wave_ids)

    while pi.wave_tx_busy():      # Wait for transmission to complete
        time.sleep(0.001)

    pi.wave_clear()               # Cleanup waveforms

def setup_pigpio_pin(pi: pigpio.pi, pin, pin_name):
    try:
        if pin_name == "STEP":
            step_pin = BCM_number[pin['number']] # pigpio assumes BCM numbering
            print('Setting STEP pin on BCM pin ',step_pin,' up with pigpio')
            pi.set_mode(step_pin, pigpio.OUTPUT)
            # print('mode set..')
            pi.set_pull_up_down(step_pin, pigpio.PUD_DOWN)
            # print('pulldown set..')
            print('STEP pin was set with internal pulldown.')

    except: 
        print(f'{pin_name} failed setup')

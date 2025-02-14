import time

class Program:
    def __init__(self, pump):
        self.pump = pump

    def parse_and_execute(self, commands):
        lines = commands.split('\n')
        for line in lines:
            if 'pump' in line:
                volume = float(line.split()[1])
                self.pump.move_volume(volume, speed=1)
            elif 'wait' in line:
                wait_time = int(line.split()[1])
                print(f"Waiting for {wait_time} seconds...")
                time.sleep(wait_time)
            elif 'repeat' in line:
                # Handle repeat logic if needed
                pass

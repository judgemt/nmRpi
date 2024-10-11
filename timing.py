import time
pulseWidth = 5E-6
pulseWidth = 0

start_time = time.time()
for i in range(9600):
    time.sleep(pulseWidth)
    pass
end_time = time.time()

print(f"Ran 9600 steps in {end_time-start_time} s.")


t1 = time.time()
for i in range(int(1E5)):
    time.sleep(0)
t2 = time.time()
sleep_overhead = (t2-t1)/1E6
print(sleep_overhead)
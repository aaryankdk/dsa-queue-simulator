# Traffic Generator for Vehicle Generation in Traffic Simulator

import time
import random

ROAD = ['A', 'B', 'C', 'D']
LANES = [1, 2, 3]
SPAWN_RATE = {
    1: 1,
    2: 2, # Normal lane with higher spawn rate
    3: 1
}

vehicle_id = 0

while True:
    vehicle_id += 1
    road = random.choice(ROAD)
    lane = random.choices(LANES, weights=[SPAWN_RATE[lane] for lane in LANES])[0] # for-in loop to select lane based on spawn rate
    print(f"ID: {vehicle_id}, Road: {road}, Lane: {lane}")  
    time.sleep(1) # Spawn Interval
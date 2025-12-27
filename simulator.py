# Simulator: Main Program for Traffic Simulation

import threading
from queue import Queue
import os
import time


GREEN_LIGHT = 10
RED_LIGHT = 10


class Vehicle:
    def __init__(self, vehicle_id, road, lane):
        self.vehicle_id = vehicle_id
        self.road = road
        self.lane = lane


class FileReaderThread(threading.Thread): # Thread to read vehicle.data
    def __init__(self, filename, queue):
        super().__init__() 
        self.filename = "vehicle.data"
        self.queue = queue
        self.daemon = True # Kills thread when main program ends
        self.running = True
        self.vehicle_id = 0

    def run(self):
        while self.running:
            try:
                if os.path.exists(self.filename):
                    with open(self.filename, 'r') as f:
                        lines=f.readlines()
                    if lines:
                        with open(self.filename, 'w') as f:
                            f.write("") # Clear file after reading
                    for line in lines:
                        line=line.strip() # Remove whitespace
                        if not line:
                            continue
                        try:
                            parts=line.split(": ") # Split ID and RoadLane
                            vehicle_id=parts[0]
                            road_lane=parts[1]
                            road=road_lane[0]
                            lane=int(road_lane[2])
                            vehicle=Vehicle(vehicle_id, road, lane)
                            if road in self.queue and lane in self.queue[road]:
                                self.queue[road][lane].enqueue(vehicle)
                                self.vehicle_id += 1
                                print(f"[FileReader] Vehicle Added: ID={vehicle_id}, Road={road}, Lane={lane}")
                        except(ValueError, IndexError) as e:
                            print(f"[FileReader] Error: {line}") # Error in vehicle data format
            except Exception as e:
                print(f"[FileReader] Error: {e}")
            time.sleep(1)
    
    def stop(self):
        self.running= False


class TrafficLight:
    def __init__(self, road):
        self.road = road
        self.state = 'RED'
        self.counter = 0

    def update(self): # Updates each second due to time.sleep(1)
        self.counter += 1
    
    def green(self):
        self.state = 'GREEN'
        self.counter = 0
    def red(self):
        self.state = 'RED'
        self.counter = 0


class TrafficLightController:
    def __init__(self, traffic_lights):
        self.traffic_lights = traffic_lights
        self.road_order = ['A', 'B', 'C', 'D']
        self.current_index = 0
        self.green_light = self.road_order[self.current_index]
        self.traffic_lights[self.road_order[self.current_index]].green()
        for road in ['B', 'C', 'D']:
            self.traffic_lights[road].red()

    def update(self):
        current_light = self.traffic_lights[self.green_light]
        current_light.update()
        if current_light.state == 'GREEN' and current_light.counter >= GREEN_LIGHT:
            current_light.red()
            self.current_index = (self.current_index + 1) % len(self.road_order)
            self.green_light = self.road_order[self.current_index]
            self.traffic_lights[self.green_light].green()


class TrafficSimulator: # Main logic for traffic simulation
    def __init__(self):
        self.queue = {
            'A': {1: Queue(), 2: Queue(), 3: Queue()},
            'B': {1: Queue(), 2: Queue(), 3: Queue()},
            'C': {1: Queue(), 2: Queue(), 3: Queue()},
            'D': {1: Queue(), 2: Queue(), 3: Queue()}
        }

        self.traffic_lights = {
            'A': TrafficLight('A'),
            'B': TrafficLight('B'),
            'C': TrafficLight('C'),
            'D': TrafficLight('D')
        }

        self.light_controller = TrafficLightController(self.traffic_lights)
        self.file_reader = FileReaderThread('vehicle.data', self.queue)
        self.file_reader.start()

    def print_status(self):
        for road in ['A', 'B', 'C', 'D']:
            l1 = self.queue[road][1].size()
            l2 = self.queue[road][2].size()
            l3 = self.queue[road][3].size()
            total = l1 + l2 + l3
            if total > 0:
                print(f"Road {road}: L1={l1} L2={l2} L3={l3} (Total: {total})")
        for road in ['A', 'B', 'C', 'D']:
            light = self.traffic_lights[road]
            print(f"Traffic Light {road}: {light.state} ({light.counter}s)")
        print("-" * 40)

    def run(self):        
        while True:
            time.sleep(1)
            self.light_controller.update()
            self.print_status()


def main():
    simulator = TrafficSimulator()
    simulator.run()


if __name__ == "__main__":
    main()
import threading
from custom_queue import Queue
import os
import time
import random
import pygame
import math


GREEN_LIGHT = 10
RED_LIGHT = 10


# Pygame settings
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 800
FPS = 60

# Colors
BACKGROUND = (66,69,73)
WHITE  = (230, 230, 230)
GRAY   = (100, 100, 100)
RED    = (220,99,99)
GREEN  = (99, 220, 99)
BLUE   = (0,146,156)
YELLOW = (255, 255, 180)
ORANGE = (255, 165, 0)


class Vehicle:
    def __init__(self, vehicle_id, road, lane):
        self.vehicle_id = vehicle_id
        self.road = road
        self.lane = lane
        self.x = 0
        self.y = 0
        self.target_x = 0
        self.target_y = 0
        self.is_moving = False
        self.move_speed = 3
        self.original_road = road
        self.original_lane = lane
        self.exiting = False
        self.turning_left = False
        self.turning_right = False
        self.at_intersection = False


class FileReaderThread(threading.Thread):
    def __init__(self, filename, queue_dict):
        super().__init__()
        self.filename = "vehicle.data"
        self.queue_dict = queue_dict
        self.daemon = True
        self.running = True
        self.vehicle_id = 0

    def run(self):
        while self.running:
            try:
                if os.path.exists(self.filename):
                    with open(self.filename, 'r') as f:
                        lines = f.readlines()
                    if lines:
                        with open(self.filename, 'w') as f:
                            f.write("")
                    for line in lines:
                        line = line.strip()
                        if not line:
                            continue
                        try:
                            parts = line.split(": ")
                            vehicle_id = parts[0]
                            road_lane = parts[1]
                            road = road_lane[0]
                            lane = int(road_lane[2])
                            vehicle = Vehicle(vehicle_id, road, lane)
                            if road in self.queue_dict and lane in self.queue_dict[road]:
                                self.queue_dict[road][lane].enqueue(vehicle)
                                self.vehicle_id += 1
                                print(f"[FileReader] Vehicle Added: ID={vehicle_id}, Road={road}, Lane={lane}")
                        except (ValueError, IndexError):
                            print(f"[FileReader] Error: {line}")
            except Exception as e:
                print(f"[FileReader] Error: {e}")
            time.sleep(1)

    def stop(self):
        self.running = False


class TrafficLight:
    def __init__(self, road):
        self.road = road
        self.state = 'RED'
        self.counter = 0

    def update(self):
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
        self.traffic_lights[self.green_light].green()
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


class VehicleProcessorThread(threading.Thread):
    def __init__(self, queue_dict, traffic_lights):
        super().__init__()
        self.queue_dict = queue_dict
        self.traffic_lights = traffic_lights
        self.daemon = True
        self.running = True
        self.moving_vehicles = []

        self.right_turn = {'A': 'D', 'B': 'A', 'C': 'B', 'D': 'C'}
        self.left_turn = {'A': 'B', 'B': 'C', 'C': 'D', 'D': 'A'}
        self.straight = {'A': 'C', 'B': 'D', 'C': 'A', 'D': 'B'}

    def run(self):
        while self.running:
            time.sleep(1)
            self.process_l3_lanes()
            self.process_l2_lanes()
            self.process_l1_lanes()

    def stop(self):
        self.running = False

    def process_l3_lanes(self):
        for road in ['A', 'B', 'C', 'D']:
            l3_queue = self.queue_dict[road][3]
            if not l3_queue.is_empty():
                vehicle = l3_queue.dequeue()
                if vehicle.x != 0 or vehicle.y != 0:
                    next_road = self.left_turn[road]
                    vehicle.original_road = vehicle.road
                    vehicle.original_lane = vehicle.lane
                    vehicle.road = next_road
                    vehicle.lane = 1
                    vehicle.is_moving = True
                    vehicle.turning_left = True
                    self.moving_vehicles.append(vehicle)
                else:
                    l3_queue.enqueue(vehicle)

    def process_l2_lanes(self):
        for road in ['A', 'B', 'C', 'D']:
            light = self.traffic_lights[road]
            l2_queue = self.queue_dict[road][2]
            if light.state == 'GREEN' and not l2_queue.is_empty():
                vehicle = l2_queue.dequeue()
                if vehicle.x != 0 or vehicle.y != 0:
                    if random.random() < 0.5:
                        next_road = self.straight[road]
                    else:
                        next_road = self.right_turn[road]
                        vehicle.turning_right = True
                    vehicle.original_road = vehicle.road
                    vehicle.original_lane = vehicle.lane
                    vehicle.road = next_road
                    vehicle.lane = 1
                    vehicle.is_moving = True
                    self.moving_vehicles.append(vehicle)
                else:
                    l2_queue.enqueue(vehicle)

    def process_l1_lanes(self):
        for road in ['A', 'B', 'C', 'D']:
            l1_queue = self.queue_dict[road][1]
            if not l1_queue.is_empty():
                l1_queue.dequeue()


class TrafficGUI:
    def __init__(self, queue_dict, traffic_lights, vehicle_processor):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Traffic Junction Simulator")
        self.clock = pygame.time.Clock()
        self.queue_dict = queue_dict
        self.traffic_lights = traffic_lights
        self.vehicle_processor = vehicle_processor
        self.font = pygame.font.Font(None, 24)

        self.center_x = WINDOW_WIDTH // 2
        self.center_y = WINDOW_HEIGHT // 2
        self.road_width = 80
        self.lane_width = self.road_width // 3

    def get_queue_position(self, road, lane, index):
        spacing = 30
        lane_offset = (lane - 1) * self.lane_width + self.lane_width // 2

        if road == 'A':
            x = self.center_x - self.road_width // 2 + lane_offset
            y = self.center_y - self.road_width // 2 - 40 - (index * spacing)
        elif road == 'C':
            x = self.center_x - self.road_width // 2 + (3 - lane) * self.lane_width + self.lane_width // 2
            y = self.center_y + self.road_width // 2 + 40 + (index * spacing)
        elif road == 'B':
            x = self.center_x + self.road_width // 2 + 40 + (index * spacing)
            y = self.center_y - self.road_width // 2 + lane_offset
        else:
            x = self.center_x - self.road_width // 2 - 40 - (index * spacing)
            y = self.center_y - self.road_width // 2 + (3 - lane) * self.lane_width + self.lane_width // 2

        return x, y

    def update_moving_vehicles(self):
        completed = []
        exited = []

        for vehicle in self.vehicle_processor.moving_vehicles:
            if vehicle.is_moving:

                if vehicle.lane == 1 and vehicle.exiting:
                    if vehicle.road == 'A':
                        vehicle.y -= vehicle.move_speed
                        if vehicle.y < -50:
                            exited.append(vehicle)
                    elif vehicle.road == 'C':
                        vehicle.y += vehicle.move_speed
                        if vehicle.y > WINDOW_HEIGHT + 50:
                            exited.append(vehicle)
                    elif vehicle.road == 'B':
                        vehicle.x += vehicle.move_speed
                        if vehicle.x > WINDOW_WIDTH + 50:
                            exited.append(vehicle)
                    elif vehicle.road == 'D':
                        vehicle.x -= vehicle.move_speed
                        if vehicle.x < -50:
                            exited.append(vehicle)
                    continue

                if vehicle.turning_left and not vehicle.at_intersection:
                    if vehicle.original_road == 'A':
                        vehicle.target_x = self.center_x - self.road_width // 2 + (3 - 1) * self.lane_width + self.lane_width // 2
                        vehicle.target_y = self.center_y - self.road_width // 2 + 5
                    elif vehicle.original_road == 'C':
                        vehicle.target_x = self.center_x - self.road_width // 2 + (1 - 1) * self.lane_width + self.lane_width // 2
                        vehicle.target_y = self.center_y + self.road_width // 2 - 5
                    elif vehicle.original_road == 'B':
                        vehicle.target_x = self.center_x + self.road_width // 2 - 5
                        vehicle.target_y = self.center_y - self.road_width // 2 + (3 - 1) * self.lane_width + self.lane_width // 2
                    elif vehicle.original_road == 'D':
                        vehicle.target_x = self.center_x - self.road_width // 2 + 5
                        vehicle.target_y = self.center_y - self.road_width // 2 + (1 - 1) * self.lane_width + self.lane_width // 2
                    
                    dx = vehicle.target_x - vehicle.x
                    dy = vehicle.target_y - vehicle.y
                    distance = math.sqrt(dx * dx + dy * dy)
                    
                    if distance < vehicle.move_speed:
                        vehicle.x = vehicle.target_x
                        vehicle.y = vehicle.target_y
                        vehicle.at_intersection = True
                    else:
                        vehicle.x += (dx / distance) * vehicle.move_speed
                        vehicle.y += (dy / distance) * vehicle.move_speed
                    continue

                if vehicle.turning_right and not vehicle.at_intersection:
                    if vehicle.original_road == 'A':
                        vehicle.target_x = self.center_x - self.road_width // 2 + (1 - 1) * self.lane_width + self.lane_width // 2
                        vehicle.target_y = self.center_y - self.road_width // 2 + 5
                    elif vehicle.original_road == 'C':
                        vehicle.target_x = self.center_x - self.road_width // 2 + (3 - 1) * self.lane_width + self.lane_width // 2
                        vehicle.target_y = self.center_y + self.road_width // 2 - 5
                    elif vehicle.original_road == 'B':
                        vehicle.target_x = self.center_x + self.road_width // 2 - 5
                        vehicle.target_y = self.center_y - self.road_width // 2 + (1 - 1) * self.lane_width + self.lane_width // 2
                    elif vehicle.original_road == 'D':
                        vehicle.target_x = self.center_x - self.road_width // 2 + 5
                        vehicle.target_y = self.center_y - self.road_width // 2 + (3 - 1) * self.lane_width + self.lane_width // 2
                    
                    dx = vehicle.target_x - vehicle.x
                    dy = vehicle.target_y - vehicle.y
                    distance = math.sqrt(dx * dx + dy * dy)
                    
                    if distance < vehicle.move_speed:
                        vehicle.x = vehicle.target_x
                        vehicle.y = vehicle.target_y
                        vehicle.at_intersection = True
                    else:
                        vehicle.x += (dx / distance) * vehicle.move_speed
                        vehicle.y += (dy / distance) * vehicle.move_speed
                    continue

                target_x, target_y = self.get_queue_position(vehicle.road, vehicle.lane, 0)
                dx = target_x - vehicle.x
                dy = target_y - vehicle.y
                distance = math.sqrt(dx * dx + dy * dy)

                if distance < vehicle.move_speed:
                    vehicle.x = target_x
                    vehicle.y = target_y
                    vehicle.is_moving = False

                    if vehicle.lane == 1:
                        vehicle.is_moving = True
                        vehicle.exiting = True
                    else:
                        self.queue_dict[vehicle.road][vehicle.lane].enqueue(vehicle)
                        completed.append(vehicle)
                else:
                    vehicle.x += (dx / distance) * vehicle.move_speed
                    vehicle.y += (dy / distance) * vehicle.move_speed

        for v in completed + exited:
            self.vehicle_processor.moving_vehicles.remove(v)

    def draw(self):
        self.screen.fill(BACKGROUND)
        self.update_moving_vehicles()
        self.draw_roads()
        self.draw_traffic_lights()
        self.draw_vehicles()
        self.draw_labels()
        pygame.display.flip()
        self.clock.tick(FPS)
    
    def draw_roads(self):
        # Vertical road
        pygame.draw.rect(self.screen, GRAY, 
                        (self.center_x - self.road_width//2, 0, self.road_width, WINDOW_HEIGHT))
        
        # Horizontal road
        pygame.draw.rect(self.screen, GRAY, 
                        (0, self.center_y - self.road_width//2, WINDOW_WIDTH, self.road_width))
        
        # Lane dividers
        for i in range(1, 3):
            x = self.center_x - self.road_width//2 + i * self.lane_width
            for y in range(0, WINDOW_HEIGHT, 20):
                pygame.draw.line(self.screen, YELLOW, (x, y), (x, y+10), 2)
        
        for i in range(1, 3):
            y = self.center_y - self.road_width//2 + i * self.lane_width
            for x in range(0, WINDOW_WIDTH, 20):
                pygame.draw.line(self.screen, YELLOW, (x, y), (x+10, y), 2)
        
        # Center junction
        pygame.draw.rect(self.screen, (150, 150, 150),
                        (self.center_x - self.road_width//2, self.center_y - self.road_width//2,
                         self.road_width, self.road_width))
    
    def draw_traffic_lights(self):
        positions = {
            'A': (self.center_x - 60, self.center_y - 60),
            'B': (self.center_x + 60, self.center_y - 60),
            'C': (self.center_x + 60, self.center_y + 60),
            'D': (self.center_x - 60, self.center_y + 60)
        }
        
        for road, pos in positions.items():
            light = self.traffic_lights[road]
            color = GREEN if light.state == 'GREEN' else RED
            pygame.draw.circle(self.screen, color, pos, 15)
            pygame.draw.circle(self.screen, WHITE, pos, 15, 2)
    
    def draw_vehicles(self):
        vehicle_width = 12
        vehicle_height = 20
        
        # Draw vehicles in queues
        for road in ['A', 'B', 'C', 'D']:
            for lane in [1, 2, 3]:
                queue = self.queue_dict[road][lane]
                
                vehicles = []
                temp_list = []
                while not queue.is_empty():
                    v = queue.dequeue()
                    vehicles.append(v)
                    temp_list.append(v)
                
                for v in temp_list:
                    queue.enqueue(v)
                
                for i, vehicle in enumerate(vehicles[:10]):
                    color = BLUE if lane == 2 else (ORANGE if lane == 3 else GREEN)
                    
                    # Update vehicle position
                    vehicle.x, vehicle.y = self.get_queue_position(road, lane, i)
                    
                    # Draw vehicle
                    if road in ['A', 'C']:
                        rect = pygame.Rect(vehicle.x - vehicle_width//2, vehicle.y - vehicle_height//2,
                                         vehicle_width, vehicle_height)
                    else:
                        rect = pygame.Rect(vehicle.x - vehicle_height//2, vehicle.y - vehicle_width//2,
                                         vehicle_height, vehicle_width)
                    
                    pygame.draw.rect(self.screen, color, rect)
                    pygame.draw.rect(self.screen, WHITE, rect, 2)
        
        # Draw moving vehicles
        for vehicle in self.vehicle_processor.moving_vehicles:
            color = BLUE if vehicle.original_lane == 2 else (ORANGE if vehicle.original_lane == 3 else GREEN)
            
            # Determine orientation based on original road
            if vehicle.original_road in ['A', 'C']:
                rect = pygame.Rect(vehicle.x - vehicle_width//2, vehicle.y - vehicle_height//2,
                                 vehicle_width, vehicle_height)
            else:
                rect = pygame.Rect(vehicle.x - vehicle_height//2, vehicle.y - vehicle_width//2,
                                 vehicle_height, vehicle_width)
            
            pygame.draw.rect(self.screen, color, rect)
            pygame.draw.rect(self.screen, WHITE, rect, 2)
    
    def draw_labels(self):
        labels = {
            'A': (self.center_x, 30),
            'B': (WINDOW_WIDTH - 50, self.center_y),
            'C': (self.center_x, WINDOW_HEIGHT - 30),
            'D': (50, self.center_y)
        }
        
        for road, pos in labels.items():
            text = self.font.render(f"Road {road}", True, WHITE)
            text_rect = text.get_rect(center=pos)
            self.screen.blit(text, text_rect)
        
        # Queue counts
        y_offset = 10
        for road in ['A', 'B', 'C', 'D']:
            l1 = self.queue_dict[road][1].size()
            l2 = self.queue_dict[road][2].size()
            l3 = self.queue_dict[road][3].size()
            text = self.font.render(f"{road}: L1={l1} L2={l2} L3={l3}", True, WHITE)
            self.screen.blit(text, (10, y_offset))
            y_offset += 25


class TrafficSimulator:
    def __init__(self):
        self.queue_dict = {
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
        self.vehicle_processor = VehicleProcessorThread(self.queue_dict, self.traffic_lights)
        self.vehicle_processor.start()
        self.file_reader = FileReaderThread('vehicle.data', self.queue_dict)
        self.file_reader.start()
        self.gui = TrafficGUI(self.queue_dict, self.traffic_lights, self.vehicle_processor)
        self.last_update = time.time()

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            
            # Update traffic lights every second
            current_time = time.time()
            if current_time - self.last_update >= 1:
                self.light_controller.update()
                self.last_update = current_time
            self.gui.draw()
        pygame.quit()


def main():
    simulator = TrafficSimulator()
    simulator.run()


if __name__ == "__main__":
    main()
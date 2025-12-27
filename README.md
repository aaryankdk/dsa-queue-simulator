# dsa-queue-simulator

A multi-threaded traffic junction simulator with priority queue management and real-time visualization using Pygame.

---

## Author

- **Name**: Aaryan Khadka
- **Roll Number**: 38
- **Class**: CS-A, II/I
- **Subject**: COMP202

---

## GIF/Video

![Visual Demonstration](dsa-queue-simulator.gif)

---

## Features

**Custom Data Structures**: Queue and Priority Queue implementations  
**Multi-threaded Architecture**: Concurrent file reading and vehicle processing  
**Dynamic Vehicle Spawning**: Vehicles enter from screen edges  
**Smart Traffic Management**: Round-robin light cycling with priority override  
**Priority Queue System**: AL2 lane gets priority when congested (≥10 vehicles)  
**Realistic Vehicle Movement**: Smooth animations with proper turning behavior  
**Real-time Visualization**: Live traffic display with Pygame  
**Lane-based Routing**: Different behavior for each lane type  

---

## Prerequisites

### Required Software
- **Python 3.7+** (recommended: Python 3.8 or higher)
- **pip** (Python package installer)

### Required Libraries
- `pygame` - For graphics and visualization
- `threading` - Built-in Python module for concurrent execution

---

## Installation

### Step 1: Clone or Download the Project
```bash
git clone https://github.com/aaryankdk/dsa-queue-simulator
cd dsa-queue-simulator
```

### Step 2: Install Dependencies
```bash
pip install pygame
```

---

## How to Run

**Terminal/Command Prompt 1:**
```bash
python traffic_generator.py
```
This starts the vehicle generator that writes to `vehicle.data` file every second.

**Terminal/Command Prompt 2:**
```bash
python simulator.py
```
This starts the traffic simulator with visualization.

### Stopping the Programs
- **Simulator**: Close the Pygame window or press `Ctrl+C` in terminal
- **Traffic Generator**: Press `Ctrl+C` in its terminal window

---

## System Overview

**traffic_generator.py**
- Generates random vehicles every second
- Writes vehicle data to `vehicle.data` file
- Format: `<vehicle_id>: <road>L<lane>`

**custom_queue.py**
- Implements Queue class (FIFO structure)
- Implements PriorityQueue class with congestion detection

**simulator.py**
- **FileReaderThread**: Monitors `vehicle.data` and spawns vehicles
- **VehicleProcessorThread**: Processes lane queues and moves vehicles
- **TrafficLightController**: Manages traffic light states and priority mode
- **TrafficGUI**: Renders visualization using Pygame

---

## Lane System

### Four-Way Junction
- **Road A**: Top (entering from North)
- **Road B**: Right (entering from East)
- **Road C**: Bottom (entering from South)
- **Road D**: Left (entering from West)

### Three-Lane System

| Lane | Color  | Behavior | Traffic Light Required |
|------|--------|----------|------------------------|
| L1   | Green  | Exit lane (removes vehicle) | No |
| L2   | Blue   | 50% straight, 50% right turn | Yes (must wait for green) |
| L3   | Orange | Always turns left | No (free flow) |

### Routing Tables

**Right Turn Mapping:**
- A → D, B → A, C → B, D → C

**Left Turn Mapping:**
- A → B, B → C, C → D, D → A

**Straight Mapping:**
- A → C, B → D, C → A, D → B

---

## Priority Queue System

### AL2 Priority Mode

**Activation Condition:**
- Triggers when AL2 (Road A, Lane 2) has **≥10 vehicles** in queue

**Behavior During Priority Mode:**
1. All traffic lights turn RED immediately
2. Road A light turns GREEN
3. Normal light cycling is suspended
4. AL2 vehicles are processed continuously
5. Visual indicator appears: "PRIORITY MODE: AL2 ACTIVE" (red text at top)
6. Console logs activation message

**Deactivation Condition:**
- Deactivates when AL2 drops to **≤5 vehicles**
- Normal round-robin light cycling resumes
- Console logs deactivation message

---

## References

1. **Multi-threading in Python**
   - Official Documentation: https://docs.python.org/3/library/threading.html
   - Used for concurrent file monitoring and vehicle processing

2. **Pygame Documentation**
   - Official Site: https://www.pygame.org/docs/
   - Used for: Window management, drawing primitives, event handling, clock/FPS control

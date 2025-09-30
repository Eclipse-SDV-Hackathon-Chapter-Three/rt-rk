# Team RT-RK Solution Plan

# 1. Your Team at a Glance

## Team Name / Tagline  
**RT-RK** - *"Driving the Future of Connected Mobility"*

## Team Members  
| Name | GitHub Handle | Role(s) |
|-------|---------------|---------|
| Sachin Kumar | @sachinkum0009 | Embedded systems |
| Luka Radovic | @r4d0v1c | Computer Vision |
| Vuk Pavic | @Vulpes107 | System Architecture |
| Blagoje Milosevic | @bagi002 | Algorithms |
| Petar Resetar | @resetarp | Dashboard Development |

## Challenge  
**Eclipse SDV Hackathon Chapter Three** - SDV Lab Challenge

## Core Idea  
Our solution builds a comprehensive Software Defined Vehicle (SDV) platform that demonstrates advanced ADAS capabilities through a modular, container-based architecture.

### Architecture Overview
- **Simulation Foundation**: CARLA simulator provides realistic driving scenarios and sensor data
- **Container Orchestration**: Ankaios manages containerized workloads on embedded systems
- **Communication Layer**: uProtocol for inter-container communication, with Zenoh for high-bandwidth, low-latency data streams
- **Intelligent Supervision**: Supervisor process dynamically spawns controllers based on driving conditions and requirements
- **Modular Design**: Independent containerized workloads for each ADAS feature

### ADAS Features Implementation
1. **Lane Keeping Assistance**
   - Camera-based lane detection using computer vision algorithms
   - Real-time image processing for lane boundary identification
   
2. **Emergency Braking System**
   - Radar-based obstacle detection and collision avoidance
   - Automatic emergency stop when collision risk is detected
   
3. **Pedestrian Detection & Safety**
   - Camera-based object detection for pedestrian identification
   - Alert and avoidance mechanisms for enhanced safety

```mermaid
graph TB
    A[CARLA Simulator] --> B[Sensor Data]
    B --> C[uProtocol/Zenoh Communication]
    C --> D[Ankaios Container Orchestrator]
    D --> E[Lane Assistance Container]
    D --> F[Emergency Stop Container]
    D --> G[Pedestrian Detection Container]
    E --> H[Vehicle Control Interface]
    F --> H
    G --> H
```

# 2. How Do You Work

## Development Process  
We follow an agile development approach with rapid prototyping and iterative improvements. Our process emphasizes collaboration, quick feedback loops, and continuous integration.

### Planning & Tracking  
- **Project Management**: GitHub Projects for task tracking and sprint planning
- **Dynamic sync**: Quick sync meetings to discuss progress and blockers when needed
- **Documentation**: Continuous documentation in markdown files and code comments

### Quality Assurance  
- **Code Reviews**: All code changes require peer review before merging
- **Testing Strategy**: Unit tests, and manual testing in Carla simulator
- **Documentation Standards**: Comprehensive README files and API documentation

## Communication  
- **Primary Channel**: WhatsApp group chat for real-time communication
- **Progress Updates**: Regular updates in team chat and project board

## Decision Making  
- **Consensus Building**: Technical decisions made through team discussion
- **Lead Consultation**: Major architectural decisions reviewed by team
- **Documentation**: All decisions documented with reasoning
- **Rapid Response**: Quick decision-making for time-sensitive issues during hackathon

# 3. Building and Running with Podman

## Prerequisites
- Podman installed on your system
- Ankaios runtime environment

## Project Structure
The project is organized with modular worker components:
```
rt-rk/
├── workers/
│   ├── emergency/
│   │   └── worker_emergency.py     # Emergency stop system
│   ├── lane/
│   │   └── worker_lane.py          # Lane keeping assistance
│   └── pedestrian/
│       └── worker_pedestrian.py    # Pedestrian detection
├── Dockerfile
├── manifest.yaml
├── requirements.txt
└── build.sh
```

## Building the Container

### Enhanced Build Script
The build script supports multiple options for different workflows:

```bash
# Basic build (container only)
./build.sh

# Build and deploy to Ankaios
./build.sh --deploy

# Rebuild and redeploy (deletes existing workloads first)
./build.sh --rebuild

# Clean up workloads without rebuilding
./build.sh --clean

# Show help
./build.sh --help
```

### Manual Build
```bash
# Build the container image
podman build -t localhost/example_python_workload:0.1 .

# Verify the build
podman images | grep example_python_workload
```

## Running the Application

### Local Testing - Individual Workers
```bash
# Test emergency stop worker
podman run --rm localhost/example_python_workload:0.1 python3 workers/emergency/worker_emergency.py

# Test lane assistance worker  
podman run --rm localhost/example_python_workload:0.1 python3 workers/lane/worker_lane.py

# Test pedestrian detection worker
podman run --rm localhost/example_python_workload:0.1 python3 workers/pedestrian/worker_pedestrian.py
```

### Deploy with Ankaios
```bash
# Deploy all workers using the manifest file
ank apply manifest.yaml

# Check workload status
ank get workloads

# Monitor specific worker logs
ank logs EmergencyStop --follow
ank logs LaneAssistance --follow
ank logs PedestrianDetection --follow
```
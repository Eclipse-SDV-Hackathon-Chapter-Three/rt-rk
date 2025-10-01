# CARLA Sensors Documentation

## Overview
CarlaSetup klasa sada podržava tri tipa senzora:
- 📷 **RGB Camera** - za live video feed
- 🚧 **Obstacle Sensor** - za detekciju prepreka do 40m
- 💥 **Collision Sensor** - za detekciju kolizija

## Obstacle Sensor

### Setup
```python
def obstacle_callback(obstacle_data):
    distance = obstacle_data['distance']
    actor_type = obstacle_data['actor_type']
    print(f"Prepreka na {distance:.1f}m: {actor_type}")

carla_setup.setup_obstacle_sensor(obstacle_callback, detection_range=40.0)
```

### Obstacle Data struktura
```python
{
    'frame': int,           # Frame broj
    'timestamp': float,     # Vreme detekcije
    'distance': float,      # Udaljenost do prepreke (metri)
    'actor': carla.Actor,   # CARLA actor objekat
    'actor_id': int,        # ID actor-a
    'actor_type': str       # Tip actor-a (vehicle, pedestrian, static)
}
```

### Karakteristike
- **Domet**: 40 metri (konfigurisano)
- **Pozicija**: 2.5m napred, 0.5m visoko od centra vozila
- **Detektuje**: vozila, pešake, statičke objekte
- **Hit radius**: 0.5m

## Collision Sensor

### Setup
```python
def collision_callback(collision_data):
    actor_type = collision_data['actor_type']
    impulse = collision_data['impulse']
    print(f"Kolizija sa: {actor_type}")

carla_setup.setup_collision_sensor(collision_callback)
```

### Collision Data struktura
```python
{
    'frame': int,           # Frame broj
    'timestamp': float,     # Vreme kolizije
    'actor': carla.Actor,   # CARLA actor sa kojim je kolizija
    'actor_id': int,        # ID actor-a
    'actor_type': str,      # Tip actor-a
    'impulse': {            # Sila udara
        'x': float,
        'y': float, 
        'z': float
    }
}
```

### Karakteristike
- **Pozicija**: Centar vozila (0,0,0)
- **Detektuje**: sve kolizije vozila
- **Impulse**: normalna sila udara u 3D prostoru

## Primer korišćenja

```python
from src.carla_setup import CarlaSetup

# Inicijalizacija
carla_setup = CarlaSetup()
carla_setup.connect_to_server()
carla_setup.spawn_vehicle()

# Obstacle detection
def on_obstacle(data):
    if data['distance'] < 10.0:  # Bliska prepreka
        print(f"⚠️  PAŽNJA! Prepreka na {data['distance']:.1f}m")

# Collision detection  
def on_collision(data):
    print(f"💥 KOLIZIJA sa {data['actor_type']}!")

# Setup senzora
carla_setup.setup_obstacle_sensor(on_obstacle, detection_range=40.0)
carla_setup.setup_collision_sensor(on_collision)

# Cleanup
carla_setup.cleanup()
```

## Napomene

- Senzori se automatski čiste u `cleanup()` metodi
- Callback funkcije se pozivaju asinhrono
- Obstacle sensor može da ima lažne detekcije na manjim objektima
- Collision sensor se aktivira tek nakon stvarne kolizije
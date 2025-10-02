# Zenoh Installation and Setup

## Prerequisites

Install Zenoh Python library:

```bash
pip install zenoh
```

**Important**: This implementation is compatible with both older and newer Zenoh versions by properly handling `ZBytes` payload objects.

## ZenohPublisher Class

Klasa `ZenohPublisher` automatski objavljuje podatke iz CARLA-e kroz Zenoh messaging sistem.

### Podržani topici:

| Topic | Opis | Podaci |
|-------|------|--------|
| `carla/tesla/camera/frame` | Camera frames | Base64 encoded images |
| `carla/tesla/sensors/obstacle_distance` | Obstacle detection | Distance in meters |
| `carla/tesla/sensors/collision_status` | Collision detection | Boolean status |
| `carla/tesla/sensors/collision_data` | Collision details | Full collision data |
| `carla/tesla/dynamics/speed` | Vehicle speed | Speed in km/h and m/s |
| `carla/tesla/dynamics/rpm` | Engine RPM | RPM and engine load |
| `carla/tesla/telemetry/full` | Complete telemetry | All vehicle data |

### Korišćenje:

```python
from src.zenoh_publisher import ZenohPublisher

# Kreiranje publisher-a
publisher = ZenohPublisher(base_topic='carla/vehicle', publish_interval=0.1)

# Povezivanje
if publisher.connect():
    print("Connected to Zenoh")

# Ažuriranje podataka (automatski se objavljuju)
publisher.update_camera_frame(camera_image)
publisher.update_obstacle_distance(obstacle_data)
publisher.update_collision_status(collision_data)
publisher.update_vehicle_data(carla_vehicle)

# Pokretanje periodičnog objavljivanja
publisher.start_publishing()

# Čišćenje
publisher.stop_publishing()
publisher.disconnect()
```

### Data Formats:

#### Camera Frame
```json
{
    "timestamp": 1234567890.123,
    "shape": [360, 640, 3],
    "dtype": "uint8",
    "data": "base64_encoded_image_data"
}
```

#### Obstacle Distance
```json
{
    "timestamp": 1234567890.123,
    "distance_meters": 25.5,
    "status": "detected"
}
```

#### Collision Status
```json
{
    "timestamp": 1234567890.123,
    "collision_detected": true,
    "status": "collision"
}
```

#### Vehicle Speed
```json
{
    "timestamp": 1234567890.123,
    "speed_kmh": 45.2,
    "speed_ms": 12.6
}
```

#### Vehicle RPM
```json
{
    "timestamp": 1234567890.123,
    "rpm": 2500,
    "engine_load": 65.0
}
```

#### Vehicle Telemetry
```json
{
    "timestamp": 1234567890.123,
    "speed_kmh": 45.2,
    "rpm": 2500,
    "throttle": 0.8,
    "brake": 0.0,
    "steer": -0.2,
    "hand_brake": false,
    "reverse": false,
    "manual_gear_shift": false,
    "gear": 3
}
```

## Subscriber Example

Pokretanje subscriber-a:

```bash
python zenoh_subscriber_example.py
```

## Configuration

### Publisher Settings
- `base_topic`: Base naziv topic-a (default: 'carla/vehicle')
- `publish_interval`: Interval objavljivanja u sekundama (default: 0.1s)

### Topic Naming Convention
```
<base_topic>/<category>/<data_type>
```

Primer:
- `carla/tesla/camera/frame`
- `carla/tesla/sensors/obstacle_distance`
- `carla/tesla/dynamics/speed`

## Performance

- Default publishing rate: 10 Hz (0.1s interval)
- Camera frames: Base64 encoded (može biti veliki podatak)
- Svi ostali podaci: JSON format
- Threading: Background publishing thread

## Troubleshooting

1. **Zenoh connection failed**: Proverite da li je Zenoh router pokrenut
2. **High CPU usage**: Povećajte `publish_interval`
3. **Large data size**: Camera frame-ovi mogu biti veliki - koristite kompresiju
4. **Missing data**: Proverite da li su senzori pravilno setup-ovani
5. **ZBytes decode error**: Ova greška je rešena u najnovijoj verziji - koristite `decode_zenoh_payload()` helper funkciju

### ZBytes Compatibility
Najnovije verzije Zenoh-a koriste `ZBytes` objekte umesto običnih string payload-a. Naša implementacija automatski prepoznaje tip payload-a i odgovarajuće ga dekodira:

```python
def decode_zenoh_payload(payload):
    if hasattr(payload, 'to_bytes'):
        return payload.to_bytes().decode('utf-8')  # ZBytes
    elif hasattr(payload, 'decode'):
        return payload.decode('utf-8')             # String
    else:
        return str(payload)                        # Already decoded
```

## Advanced Usage

### Custom Topics
```python
publisher = ZenohPublisher(base_topic='my_custom/topic')
```

### Selective Publishing
```python
# Publish only specific data types by calling individual methods
publisher.publish_vehicle_speed()
publisher.publish_obstacle_distance()
```

### Custom Intervals
```python
# Fast publishing for critical data
publisher = ZenohPublisher(publish_interval=0.05)  # 20 Hz
```
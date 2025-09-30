# ucar_pub - uProtocol Hello World Example

This project demonstrates a simple publisher-subscriber pattern using uProtocol with Zenoh transport in Rust.

## Overview

- **ucar_pub**: A publisher that sends "Hello World" messages every 2 seconds using uProtocol
- **ucar_sub**: A subscriber that listens for and displays the "Hello World" messages

## Prerequisites

- Rust (latest stable version)
- Cargo

## Project Structure

```
rust_ws/
├── Cargo.toml          # Workspace configuration
├── ucar_pub/
│   ├── Cargo.toml      # Package configuration
│   └── src/
│       ├── ucar_pub.rs # Publisher implementation
│       └── ucar_sub.rs # Subscriber implementation
└── README.md           # This file
```

## Building the Project

Navigate to the workspace directory and build all binaries:

```bash
cd rust_ws
cargo build
```

This will compile both the publisher and subscriber binaries.

## Running the Examples

### Option 1: Run Publisher and Subscriber Together

1. **Start the Subscriber** (in terminal 1):
   ```bash
   cd rust_ws
   cargo run --bin ucar_sub
   ```
   
   You should see output like:
   ```
   🚀 Starting ucar_sub Hello World subscriber using uProtocol...
   ✅ uProtocol transport initialized successfully
   👂 Listening for Hello World messages from ucar_pub...
   Press Ctrl+C to stop
   ```

2. **Start the Publisher** (in terminal 2):
   ```bash
   cd rust_ws
   cargo run --bin ucar_pub
   ```
   
   You should see output like:
   ```
   🚀 Starting ucar_pub Hello World publisher using uProtocol...
   ✅ uProtocol transport initialized successfully
   📡 Sent: "Hello World from ucar_pub! Message #1"
   📡 Sent: "Hello World from ucar_pub! Message #2"
   ```

3. **Observe the Communication**: The subscriber terminal should start receiving messages:
   ```
   📨 Received: "Hello World from ucar_pub! Message #1" (#1) at timestamp 1759260067
   📨 Received: "Hello World from ucar_pub! Message #2" (#2) at timestamp 1759260069
   ```

### Option 2: Run Individual Components

#### Publisher Only
```bash
cd rust_ws
cargo run --bin ucar_pub
```

#### Subscriber Only
```bash
cd rust_ws
cargo run --bin ucar_sub
```

## How It Works

### Publisher (ucar_pub)
- Initializes a uProtocol transport with Zenoh backend
- Creates a UUri for message routing
- Publishes JSON-serialized "Hello World" messages every 2 seconds
- Each message includes:
  - Custom message text
  - Timestamp
  - Incrementing counter

### Subscriber (ucar_sub)
- Initializes the same uProtocol transport
- Subscribes to the same UUri as the publisher
- Deserializes incoming JSON messages
- Displays received messages with details

### uProtocol Configuration
- **Authority**: "ucar"
- **Entity ID**: 0x00010001
- **Version**: 1
- **Resource ID**: 0x8000
- **Transport**: Zenoh (peer mode with multicast discovery)

## Message Format

```json
{
  "message": "Hello World from ucar_pub! Message #1",
  "timestamp": 1759260067,
  "counter": 1
}
```

## Stopping the Applications

Press `Ctrl+C` in each terminal to stop the publisher and subscriber.

## Dependencies

The project uses the following key dependencies:
- `up-rust`: uProtocol core library
- `up-transport-zenoh`: Zenoh transport implementation for uProtocol
- `zenoh`: High-performance pub/sub messaging
- `tokio`: Async runtime
- `serde`: Serialization framework
- `log` & `env_logger`: Logging utilities

## Troubleshooting

1. **Build Errors**: Ensure you have the latest Rust toolchain installed
2. **Network Issues**: Check that multicast is enabled on your network interface
3. **No Messages Received**: Ensure both publisher and subscriber use the same UUri configuration

## Next Steps

This example can be extended to:
- Add more complex message types
- Implement multiple publishers/subscribers
- Add authentication and security
- Integrate with real sensor data
- Scale to distributed systems

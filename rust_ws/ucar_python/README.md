# ucar_python - Python bindings for ucar uProtocol subscriber

This project provides Python bindings for the Rust-based ucar uProtocol subscriber, allowing you to receive Hello World messages from the `ucar_pub` publisher directly in Python code.

## Features

- **PyO3 Integration**: Seamless Rust-Python interoperability
- **Async Support**: Full async/await support using pyo3-asyncio
- **Callback-based**: Register Python functions to handle incoming messages
- **uProtocol Compatible**: Uses the same uProtocol/Zenoh transport as the Rust implementation

## Prerequisites

- **Python 3.8+**
- **Rust** (for building the extension)
- **Maturin** (for building Python extensions from Rust)

## Installation

### 1. Install Maturin

```bash
pip install maturin
```

### 2. Build and Install the Extension

From the `ucar_python` directory:

```bash
# Development build (creates symlinks for development)
maturin develop

# Or for production build
maturin build --release
pip install target/wheels/ucar_python-*.whl
```

## Usage

### Basic Example

```python
import asyncio
from ucar_python import UCarSubscriber

async def main():
    # Create subscriber
    subscriber = UCarSubscriber()
    
    # Initialize transport
    await subscriber.initialize()
    
    # Define message handler
    def on_message(msg):
        print(f"Received: {msg['message']}")
        print(f"Counter: {msg['counter']}")
        print(f"Timestamp: {msg['timestamp']}")
    
    # Start listening
    await subscriber.start_listening(on_message)
    
    # Keep running (in real app, you'd have other logic here)
    await asyncio.sleep(60)

if __name__ == "__main__":
    asyncio.run(main())
```

### Running the Complete Example

1. **Start the Rust publisher** (in another terminal):
   ```bash
   cd ../ucar_pub
   cargo run --bin ucar_pub
   ```

2. **Run the Python subscriber**:
   ```bash
   python example_subscriber.py
   ```

## Message Format

The subscriber receives messages with the following structure:

```python
{
    "message": "Hello World from ucar_pub! Message #1",
    "timestamp": 1727820000,  # Unix timestamp
    "counter": 1              # Message counter from publisher
}
```

## Architecture

```
┌─────────────────┐    uProtocol/Zenoh    ┌─────────────────┐
│   ucar_pub      │ ──────────────────→   │  ucar_python    │
│   (Rust)        │    Hello Messages     │  (Rust + PyO3)  │
└─────────────────┘                       └─────────────────┘
                                                    │
                                               Python API
                                                    │
                                                    ▼
                                          ┌─────────────────┐
                                          │ Python Script   │
                                          │ (Your Code)     │
                                          └─────────────────┘
```

## Class Reference

### `UCarSubscriber`

#### Methods

- **`__init__()`**: Create a new subscriber instance
- **`initialize()`**: Initialize the uProtocol transport (async)
- **`start_listening(callback)`**: Start listening with a Python callback (async)
- **`is_initialized()`**: Check if transport is initialized (returns bool)

#### Callback Function

Your callback function should accept one parameter:

```python
def my_callback(message: dict):
    # message contains: 'message', 'timestamp', 'counter'
    pass
```

## Development

### Project Structure

```
ucar_python/
├── Cargo.toml                 # Rust dependencies and crate config
├── pyproject.toml            # Python packaging config
├── src/
│   └── lib.rs               # Main PyO3 wrapper implementation
├── python/
│   └── __init__.py          # Python package initialization
├── example_subscriber.py    # Complete usage example
└── README.md               # This file
```

### Building for Development

```bash
# Clean build
cargo clean

# Development build with debug symbols
maturin develop

# Run example
python example_subscriber.py
```

### Troubleshooting

1. **Import Error**: Make sure you've run `maturin develop` successfully
2. **Transport Errors**: Ensure the Rust publisher is running and using the same authority ("ucar")
3. **No Messages**: Check that both publisher and subscriber are using the same UUri configuration

## Dependencies

### Rust Dependencies
- `pyo3`: Python-Rust FFI
- `pyo3-asyncio`: Async support for PyO3
- `up-rust`: uProtocol Rust implementation
- `up-transport-zenoh`: Zenoh transport for uProtocol
- `serde`: Serialization framework

### Python Dependencies
- `maturin`: For building the extension
- Python 3.8+ standard library
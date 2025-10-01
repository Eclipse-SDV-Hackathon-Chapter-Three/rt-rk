# Complete Build and Usage Guide for ucar_python

This guide provides complete instructions for building and using the PyO3 wrapper that allows Python code to access data from the Rust ucar_sub subscriber.

## 🚀 Quick Start

### Prerequisites
- **Rust** (installed via rustup)
- **Python 3.8+**
- **Maturin** (for building Python extensions)

### 1. Build the Python Extension

```bash
# Navigate to the ucar_python directory
cd /home/asus/zzzzz/hackathon/sdv_hackathon2/rt-rk/rust_ws/ucar_python

# Install maturin (if not already installed)
pip install maturin

# Build and install the extension in development mode
maturin develop

# This creates a Python module that can be imported as 'ucar_python'
```

### 2. Test the Installation

```python
# Test that the module can be imported
python -c "import ucar_python; print('✅ ucar_python imported successfully')"
```

### 3. Run the Example

**Terminal 1** - Start the Rust Publisher:
```bash
cd /home/asus/zzzzz/hackathon/sdv_hackathon2/rt-rk/rust_ws
cargo run --bin ucar_pub
```

**Terminal 2** - Run the Python Subscriber:
```python
import ucar_python
import time

def message_callback(message):
    print(f"📨 Received: {message['message']}")
    print(f"   Counter: {message['counter']}")
    print(f"   Timestamp: {message['timestamp']}")

# Create and initialize subscriber
subscriber = ucar_python.UCarSubscriber()
subscriber.initialize()

# Start listening
subscriber.start_listening(message_callback)

# Keep running
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Goodbye!")
```

## 📋 Architecture Overview

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
                                          │ Your Python App │
                                          │                 │
                                          └─────────────────┘
```

## 🛠️ Development Workflow

### Building for Development
```bash
# Clean build (if needed)
cargo clean

# Development build with hot reload
maturin develop

# Your Python code can now import ucar_python
```

### Building for Production
```bash
# Build wheel
maturin build --release

# Install the wheel
pip install target/wheels/ucar_python-*.whl
```

## 📖 API Reference

### `UCarSubscriber` Class

#### Constructor
```python
subscriber = ucar_python.UCarSubscriber()
```

#### Methods

**`initialize()`**
- Initializes the uProtocol transport connection
- Must be called before `start_listening()`
- Returns: None
- Raises: `RuntimeError` if initialization fails

```python
subscriber.initialize()
```

**`start_listening(callback)`**
- Starts listening for messages with a Python callback function
- Parameters:
  - `callback`: Function that accepts one parameter (the message dictionary)
- Returns: None
- Raises: `RuntimeError` if transport not initialized

```python
def my_callback(message):
    print(message)

subscriber.start_listening(my_callback)
```

**`is_initialized()`**
- Checks if the transport has been initialized
- Returns: `bool`

```python
if subscriber.is_initialized():
    print("Ready to listen!")
```

### Message Format

Messages received by your callback function have this structure:

```python
{
    "message": "Hello World from ucar_pub! Message #1",
    "timestamp": 1759307061,  # Unix timestamp
    "counter": 1              # Message sequence number
}
```

## 🔧 Advanced Usage

### Custom Message Handler Class

```python
import ucar_python

class MessageProcessor:
    def __init__(self):
        self.received_count = 0
        self.subscriber = ucar_python.UCarSubscriber()
    
    def setup(self):
        """Initialize the subscriber"""
        self.subscriber.initialize()
        self.subscriber.start_listening(self.handle_message)
        print("🎯 Message processor ready!")
    
    def handle_message(self, message):
        """Process received messages"""
        self.received_count += 1
        
        print(f"📦 Message {self.received_count}:")
        print(f"   Content: {message['message']}")
        print(f"   From Publisher #{message['counter']}")
        print(f"   Received at: {message['timestamp']}")
        
        # Add your custom processing here
        if "Hello" in message['message']:
            print("   👋 It's a greeting!")

# Usage
processor = MessageProcessor()
processor.setup()

# Keep running
import time
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print(f"\n📊 Total messages processed: {processor.received_count}")
```

### Async Integration (if needed)

```python
import asyncio
import ucar_python

class AsyncMessageHandler:
    def __init__(self):
        self.subscriber = ucar_python.UCarSubscriber()
        self.message_queue = asyncio.Queue()
    
    def setup(self):
        self.subscriber.initialize()
        self.subscriber.start_listening(self.queue_message)
    
    def queue_message(self, message):
        """Queue message for async processing"""
        asyncio.create_task(self.message_queue.put(message))
    
    async def process_messages(self):
        """Async message processor"""
        while True:
            message = await self.message_queue.get()
            # Async processing here
            print(f"Async processing: {message['message']}")
            await asyncio.sleep(0.1)  # Simulate async work

# Usage
async def main():
    handler = AsyncMessageHandler()
    handler.setup()
    
    # Start async processing
    await handler.process_messages()

if __name__ == "__main__":
    asyncio.run(main())
```

## 🐛 Troubleshooting

### Common Issues

**1. Import Error**
```
ImportError: No module named 'ucar_python'
```
**Solution:** Run `maturin develop` to build and install the module.

**2. Transport Initialization Fails**
```
RuntimeError: Unable to build UPTransportZenoh
```
**Solution:** Make sure no other instances are running on the same ports.

**3. No Messages Received**
- Ensure `ucar_pub` is running and publishing messages
- Check that both publisher and subscriber use the same authority ("ucar")
- Verify network connectivity if running on different machines

**4. Python Callback Errors**
Make sure your callback function:
- Accepts exactly one parameter
- Doesn't raise exceptions (they will be logged but not propagate)

### Debug Mode

Enable Rust logging to see detailed information:

```bash
RUST_LOG=info python your_script.py
```

### Performance Tips

- Keep callback functions lightweight
- For heavy processing, queue messages and process them separately
- Use async patterns for I/O-bound operations in callbacks

## 📁 Project Structure

```
ucar_python/
├── Cargo.toml                 # Rust dependencies and PyO3 config
├── pyproject.toml            # Python packaging configuration
├── src/
│   └── lib.rs               # Main PyO3 wrapper implementation
├── python/
│   └── __init__.py          # Python package initialization
├── test_ucar_python.py      # Basic functionality test
├── example_subscriber.py    # Complete usage example
└── README.md               # Detailed documentation
```

## 🚦 Next Steps

1. **Extend the Message Types**: Modify the Rust code to handle different message structures
2. **Add Error Handling**: Implement comprehensive error handling in your Python callbacks
3. **Create Multiple Subscribers**: Subscribe to different topics/URIs
4. **Add Configuration**: Make transport settings configurable from Python

## 🤝 Contributing

To modify or extend the PyO3 wrapper:

1. Edit `src/lib.rs` for Rust-side changes
2. Run `maturin develop` to rebuild
3. Test your changes with Python scripts
4. Update documentation as needed

The integration successfully provides a bridge between the Rust uProtocol/Zenoh ecosystem and Python applications!
#!/usr/bin/env python3
"""
Example script demonstrating how to use the ucar_python module
to receive messages from the Rust ucar_sub subscriber.

This script shows how to:
1. Initialize the ucar subscriber
2. Set up a callback function to handle received messages
3. Start listening for messages asynchronously
"""

#!/usr/bin/env python3
"""
Example script demonstrating how to use the ucar_python module
to receive messages from the Rust ucar_sub subscriber.

This script shows how to:
1. Initialize the ucar subscriber
2. Set up a callback function to handle received messages
3. Start listening for messages
"""

import signal
import sys
import time
from typing import Any, Dict

# Flag to track if ucar_python is available
ucar_python_available = False
UCarSubscriber = None

# Try to import our PyO3 wrapper
try:
    import ucar_python
    UCarSubscriber = ucar_python.UCarSubscriber
    ucar_python_available = True
except ImportError:
    pass

class MessageHandler:
    """Handles received messages from the ucar subscriber"""
    
    def __init__(self):
        self.message_count = 0
    
    def on_message_received(self, message: Dict[str, Any]):
        """
        Callback function that gets called when a message is received.
        
        Args:
            message: Dictionary containing:
                - message: The hello world message string
                - timestamp: Unix timestamp when message was sent
                - counter: Message counter from the publisher
        """
        self.message_count += 1
        
        print(f"🎯 Message #{self.message_count} received!")
        print(f"   Content: {message['message']}")
        print(f"   Publisher Counter: {message['counter']}")
        print(f"   Timestamp: {message['timestamp']}")
        print("   ---")

def main():
    """Main function that runs the subscriber"""
    
    print("🚀 Starting ucar_python example...")
    print("This will connect to the ucar publisher and receive Hello World messages.")
    print("Make sure the ucar_pub is running in another terminal!")
    print("Press Ctrl+C to stop.\n")
    
    # Create message handler
    handler = MessageHandler()
    
    # Create subscriber instance
    subscriber = UCarSubscriber()
    
    # Flag for graceful shutdown
    running = True
    
    def signal_handler(signum, frame):
        nonlocal running
        print("\n🛑 Received shutdown signal...")
        running = False
    
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Initialize the transport
        print("🔧 Initializing uProtocol transport...")
        subscriber.initialize()
        print("✅ Transport initialized successfully!\n")
        
        # Check if initialization was successful
        if not subscriber.is_initialized():
            print("❌ Subscriber initialization failed!")
            return
        
        # Start listening with our callback
        print("👂 Starting to listen for messages...")
        subscriber.start_listening(handler.on_message_received)
        print("✅ Listening started successfully!\n")
        
        # Keep the program running
        print("🔄 Waiting for messages... (Press Ctrl+C to stop)")
        
        # Main loop - keep running until interrupted
        while running:
            time.sleep(0.1)  # Small sleep to prevent busy waiting
        
    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user")
    except Exception as e:
        print(f"❌ Error occurred: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("\n📊 Final Statistics:")
        print(f"   Total messages received: {handler.message_count}")
        print("👋 Goodbye!")

if __name__ == "__main__":
    main()
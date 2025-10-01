#!/usr/bin/env python3
"""
Simple test script to verify the ucar_python module works correctly.
"""

import signal
import time
from typing import Any, Dict

import ucar_python

def message_callback(message):
    """Callback function to handle received messages."""
    print(f"🎯 Received message: {message}")

def main():
    """Test the ucar_python module."""
    
    print("🧪 Testing ucar_python module...")
    
    # Create subscriber instance
    try:
        subscriber = ucar_python.UCarSubscriber()
        print("✅ UCarSubscriber instance created successfully")
        
        # Test initialization
        print("🔧 Initializing transport...")
        subscriber.initialize()
        print("✅ Transport initialized")
        
        # Check status
        is_init = subscriber.is_initialized()
        print(f"📊 Initialization status: {is_init}")
        
        if is_init:
            print("👂 Starting to listen for messages...")
            subscriber.start_listening(message_callback)
            print("✅ Started listening")
            
            print("🔄 Waiting for messages for 10 seconds...")
            print("   (Make sure ucar_pub is running to see messages)")
            
            # Wait for some time to receive messages
            time.sleep(10)
            
        print("🏁 Test completed successfully!")
            
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
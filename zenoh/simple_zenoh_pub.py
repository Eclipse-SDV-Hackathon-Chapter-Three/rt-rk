#!/usr/bin/env python3

"""
Simple Zenoh Publisher

This script continuously publishes "hello world" messages to the "Hello" topic
via Zenoh every second.

Usage:
    python simple_zenoh_pub.py [--router IP_ADDRESS]

Controls:
    - Press Ctrl+C to stop the publisher
"""

import argparse
import json
import time
import zenoh


class SimplePublisher:
    def __init__(self, router_ip="127.0.0.1"):
        """
        Initialize the simple publisher.
        
        Args:
            router_ip: IP address of the Zenoh router
        """
        self.router_ip = router_ip
        self.message_count = 0
        self.topic = "Hello"
        self.message = "hello world"
        
        # Initialize Zenoh session
        self._setup_zenoh()
        
    def _setup_zenoh(self):
        """Setup Zenoh session and publisher."""
        try:
            # Configure Zenoh
            zenoh_config = zenoh.Config()
            zenoh_config.insert_json5("mode", json.dumps("peer"))
            zenoh_config.insert_json5("connect/endpoints", json.dumps([f"tcp/{self.router_ip}:7447"]))

            # Enable scouting for automatic router discovery
            zenoh_config.insert_json5("scouting/multicast/enabled", json.dumps(True))
            zenoh_config.insert_json5("scouting/gossip/enabled", json.dumps(True))
            zenoh_config.insert_json5("scouting/timeout", json.dumps(3000))  # 3 seconds timeout
            

            
            
            # Open session
            self.session = zenoh.open(zenoh_config)
            print(f"Connected to Zenoh router at {self.router_ip}:7447")
            
            # Create publisher
            self.publisher = self.session.declare_publisher(self.topic)
            print(f"Created publisher for topic: {self.topic}")
            
        except Exception as e:
            print(f"[ERROR] Failed to setup Zenoh: {e}")
            raise
    
    def start_publishing(self):
        """Start publishing messages continuously every second."""
        try:
            print(f"Starting to publish '{self.message}' to topic '{self.topic}' every second...")
            print("Press Ctrl+C to stop")
            
            while True:
                # Create message with timestamp and count
                timestamp = int(time.time() * 1000)  # milliseconds
                message_data = {
                    "data": self.message,
                    "timestamp": timestamp,
                    "count": self.message_count
                }
                
                # Convert to JSON string
                message_json = json.dumps(message_data)
                
                # Publish the message
                self.publisher.put(message_json)
                
                # Update counter and log
                self.message_count += 1
                print(f"[{timestamp}] Published message #{self.message_count}: '{self.message}'")
                
                # Wait for 1 second
                time.sleep(1.0)
                
        except KeyboardInterrupt:
            print("\nShutdown requested by user")
        except Exception as e:
            print(f"[ERROR] Publishing error: {e}")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean up resources."""
        try:
            if hasattr(self, 'publisher'):
                self.publisher.undeclare()
            if hasattr(self, 'session'):
                self.session.close()
            print("Cleanup completed")
        except Exception as e:
            print(f"[ERROR] Cleanup failed: {e}")


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Simple Zenoh Publisher')
    parser.add_argument(
        '--router',
        default='127.0.0.1',
        help='IP address of the Zenoh router (default: 127.0.0.1)'
    )
    
    args = parser.parse_args()
    
    print("Simple Zenoh Publisher")
    print("=" * 50)
    print(f"Router: {args.router}:7447")
    print(f"Topic: Hello")
    print(f"Message: hello world")
    print(f"Interval: 1 second")
    print("=" * 50)
    
    try:
        publisher = SimplePublisher(args.router)
        publisher.start_publishing()
    except KeyboardInterrupt:
        print("\nShutdown requested by user")
    except Exception as e:
        print(f"[ERROR] Failed to start publisher: {e}")


if __name__ == '__main__':
    main()

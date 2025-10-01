#!/usr/bin/env python3

"""
Simple Zenoh Subscriber

This script subscribes to "hello world" messages from the "Hello" topic
via Zenoh and displays them in real-time.

Usage:
    python simple_zenoh_sub.py [--router IP_ADDRESS]

Controls:
    - Press Ctrl+C to stop the subscriber
"""

import argparse
import json
import zenoh
import time


class SimpleSubscriber:
    def __init__(self, router_ip="127.0.0.1"):
        """
        Initialize the simple subscriber.
        
        Args:
            router_ip: IP address of the Zenoh router
        """
        self.router_ip = router_ip
        self.topic = "Hello"
        self.message_count = 0
        self.last_message_time = None
        
        # Initialize Zenoh session
        self._setup_zenoh()
        
    def _setup_zenoh(self):
        """Setup Zenoh session and subscriber."""
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
            
            # Create subscriber
            self.subscriber = self.session.declare_subscriber(
                self.topic, 
                self._message_callback
            )
            print(f"Subscribed to topic: {self.topic}")
            
        except Exception as e:
            print(f"[ERROR] Failed to setup Zenoh: {e}")
            raise
    
    def _message_callback(self, sample):
        """
        Callback function for received messages.
        
        Args:
            sample: Zenoh sample containing the message data
        """
        try:
            # Parse the message payload
            if hasattr(sample.payload, 'to_string'):
                message_str = sample.payload.to_string()
            else:
                # Handle bytes payload directly
                message_str = sample.payload.decode('utf-8') if isinstance(sample.payload, bytes) else str(sample.payload)
            
            # Try to parse as JSON
            try:
                message_data = json.loads(message_str)
                data = message_data.get("data", message_str)
                timestamp = message_data.get("timestamp", int(time.time() * 1000))
                count = message_data.get("count", "unknown")
                
                # Calculate time since last message
                current_time = time.time()
                if self.last_message_time is not None:
                    time_diff = current_time - self.last_message_time
                    interval_str = f" (+{time_diff:.2f}s)"
                else:
                    interval_str = ""
                
                self.last_message_time = current_time
                
                print(f"[{timestamp}] Received message #{count}: '{data}'{interval_str}")
                
            except json.JSONDecodeError:
                # If not JSON, treat as plain text
                timestamp = int(time.time() * 1000)
                print(f"[{timestamp}] Received plain message: '{message_str}'")
            
            # Update our local counter
            self.message_count += 1
            
        except Exception as e:
            print(f"[ERROR] Failed to process message: {e}")
    
    def start_listening(self):
        """Start listening for messages."""
        try:
            print(f"Listening for messages on topic '{self.topic}'...")
            print("Press Ctrl+C to stop")
            print("-" * 60)
            
            # Keep the subscriber running
            while True:
                time.sleep(0.1)  # Small sleep to prevent busy waiting
                
        except KeyboardInterrupt:
            print(f"\nReceived {self.message_count} messages total")
            print("Shutdown requested by user")
        except Exception as e:
            print(f"[ERROR] Listening error: {e}")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean up resources."""
        try:
            if hasattr(self, 'subscriber'):
                self.subscriber.undeclare()
            if hasattr(self, 'session'):
                self.session.close()
            print("Cleanup completed")
        except Exception as e:
            print(f"[ERROR] Cleanup failed: {e}")


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Simple Zenoh Subscriber')
    parser.add_argument(
        '--router',
        default='127.0.0.1',
        help='IP address of the Zenoh router (default: 127.0.0.1)'
    )
    
    args = parser.parse_args()
    
    print("Simple Zenoh Subscriber")
    print("=" * 50)
    print(f"Router: {args.router}:7447")
    print(f"Topic: Hello")
    print("=" * 50)
    
    try:
        subscriber = SimpleSubscriber(args.router)
        subscriber.start_listening()
    except KeyboardInterrupt:
        print("\nShutdown requested by user")
    except Exception as e:
        print(f"[ERROR] Failed to start subscriber: {e}")


if __name__ == '__main__':
    main()
import time
import sys
import logging
import signal
from src.obstacle_detection import ObstacleDetectionSystem

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('EmergencyStop')

class EmergencyStopWorker:
    def __init__(self):
        self.running = True
        self.cycle_time = 0.1  # High frequency for emergency detection (100ms)
        self.setup_signal_handlers()
        
    def setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        #signal.signal(signal.SIGTERM, self.signal_handler)
        #signal.signal(signal.SIGINT, self.signal_handler)
        
    def signal_handler(self, signum, frame):
        """Handle shutdown signals from Ankaios"""
        signal_name = signal.Signals(signum).name
        logger.info(f"Received {signal_name} signal, initiating graceful shutdown")
        self.running = False
        
    def initialize(self):
        """Initialize the worker - setup connections, load models, etc."""
        logger.info("Initializing EmergencyStop worker")
        self.obstacle_system = ObstacleDetectionSystem(debugging=True)
        logger.info("EmergencyStop worker initialized successfully")
    
    def process_cycle(self):
        """Main processing cycle - implement your worker logic here"""
        try:
            # Add your main processing logic here
            logger.debug("Processing emergency stop cycle")

            self.obstacle_system.process_obstacle_detection()

            # Example: monitor sensors, check for obstacles, analyze emergency conditions
            # emergency_detected = self.check_emergency_conditions()
            # if emergency_detected:
            #     self.trigger_emergency_stop()
            
        except Exception as e:
            logger.error(f"Error in processing cycle: {e}")
    
    def cleanup(self):
        """Cleanup resources before shutdown"""
        logger.info("Cleaning up EmergencyStop worker")
        # Add cleanup code here
        
    def run(self):
        """Main worker loop"""
        try:
            self.initialize()
            
            logger.info("Starting EmergencyStop worker main loop")
            while self.running:
                self.process_cycle()
                
                # Sleep in small chunks to allow responsive signal handling
                sleep_time = self.cycle_time
                while sleep_time > 0 and self.running:
                    chunk = min(0.05, sleep_time)  # Smaller chunks for high-frequency worker
                    time.sleep(chunk)
                    sleep_time -= chunk
                
        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt")
            self.running = False
        except Exception as e:
            logger.error(f"Fatal error in worker: {e}")
        finally:
            self.cleanup()
            logger.info("EmergencyStop worker stopped")

if __name__ == '__main__':
    worker = EmergencyStopWorker()
    worker.run()
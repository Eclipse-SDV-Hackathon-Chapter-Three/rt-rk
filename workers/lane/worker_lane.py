import time
import sys
import logging
import signal

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('LaneAssistance')

class LaneAssistanceWorker:
    def __init__(self):
        self.running = True
        self.cycle_time = 0.5  # Medium frequency for lane detection (500ms)
        self.setup_signal_handlers()
        
    def setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        signal.signal(signal.SIGTERM, self.signal_handler)
        signal.signal(signal.SIGINT, self.signal_handler)
        
    def signal_handler(self, signum, frame):
        """Handle shutdown signals from Ankaios"""
        signal_name = signal.Signals(signum).name
        logger.info(f"Received {signal_name} signal, initiating graceful shutdown")
        self.running = False
        
    def initialize(self):
        """Initialize the worker - setup connections, load models, etc."""
        logger.info("Initializing LaneAssistance worker")
        # Add your initialization code here
        time.sleep(0.5)  # Simulate initialization time
        logger.info("LaneAssistance worker initialized successfully")
    
    def process_cycle(self):
        """Main processing cycle - implement your worker logic here"""
        try:
            # Add your main processing logic here
            logger.info("Processing lane assistance cycle")
            
            # Simulate processing time
            time.sleep(0.2)
            
            # Example: analyze camera feed, detect lane markings, calculate corrections
            # lane_data = self.detect_lane_markings()
            # steering_correction = self.calculate_steering_correction(lane_data)
            # self.publish_steering_commands(steering_correction)
            
        except Exception as e:
            logger.error(f"Error in processing cycle: {e}")
    
    def cleanup(self):
        """Cleanup resources before shutdown"""
        logger.info("Cleaning up LaneAssistance worker")
        # Add cleanup code here
        
    def run(self):
        """Main worker loop"""
        try:
            self.initialize()
            
            logger.info("Starting LaneAssistance worker main loop")
            while self.running:
                self.process_cycle()
                
                # Sleep in small chunks to allow responsive signal handling
                sleep_time = self.cycle_time
                while sleep_time > 0 and self.running:
                    chunk = min(0.1, sleep_time)
                    time.sleep(chunk)
                    sleep_time -= chunk
                
        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt")
            self.running = False
        except Exception as e:
            logger.error(f"Fatal error in worker: {e}")
        finally:
            self.cleanup()
            logger.info("LaneAssistance worker stopped")

if __name__ == '__main__':
    worker = LaneAssistanceWorker()
    worker.run()
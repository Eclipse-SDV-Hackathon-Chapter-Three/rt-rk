import time
import sys
import os
import logging
import signal

from src.accident_recorder import AccidentRecorder

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('RONA')

class RONAWorker:
    def __init__(self):
        self.running = True
        self.cycle_time = 1.0 / 15.0  # 15 FPS cycle time for real-time processing
        self.recorder = None
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
        logger.info("Initializing RONA worker")
        try:
            # Create accident recordings directory if it doesn't exist
            recordings_dir = "./data/accident_recordings"
            os.makedirs(recordings_dir, exist_ok=True)
            
            # Initialize AccidentRecorder with configuration
            self.recorder = AccidentRecorder(
                fps=15,
                frame_width=640,
                frame_height=360,
                save_directory=recordings_dir
            )
            logger.info("RONA worker initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize RONA worker: {e}")
            raise
    
    def process_cycle(self):
        """Main processing cycle - implement your worker logic here"""
        try:
            if self.recorder is None:
                logger.error("Recorder not initialized")
                return False
            
            # Process one cycle of accident recording
            success = self.recorder.run()
            
            if not success:
                logger.warning("Failed to process recording cycle")
            
            return success
            
        except Exception as e:
            logger.error(f"Error in processing cycle: {e}")
            return False
    
    def cleanup(self):
        """Cleanup resources before shutdown"""
        logger.info("Cleaning up RONA worker")
        try:
            if self.recorder:
                # Get final status before cleanup
                status = self.recorder.get_status()
                logger.info(f"Final recorder status: {status}")
                
                # Any additional cleanup if needed
                # self.recorder could have cleanup methods if implemented
                
            logger.info("RONA worker cleanup completed")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
        
    def run(self):
        """Main worker loop"""
        try:
            self.initialize()
            
            logger.info("Starting RONA worker main loop")
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
            logger.info("RONA worker stopped")

if __name__ == '__main__':
    worker = RONAWorker()
    worker.run()
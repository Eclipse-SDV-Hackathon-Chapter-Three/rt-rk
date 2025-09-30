import time
import sys
import logging
import signal
import os

# POTPUNO ONEMOGUĆI QT I FORSIRAJ NON-GUI MODE
os.environ['OPENCV_VIDEOIO_PRIORITY'] = 'ffmpeg,v4l2'
os.environ['OPENCV_VIDEOIO_PRIORITY_MSMF'] = '0'
os.environ['OPENCV_LOG_LEVEL'] = 'ERROR'
os.environ['DISPLAY'] = ''

# OVO JE KLJUČNO: Import OpenCV i odmah konfiguriši
import cv2
# Onemogući threading i GUI features
cv2.setNumThreads(0)
cv2.setUseOptimized(True)

from ultralytics import YOLO

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('PedestrianDetection')

class PedestrianDetector:
    def __init__(self, model_path="yolo11n.pt", confidence_threshold=0.7):
        """Initialize the pedestrian detector with YOLO model"""
        self.model_path = model_path
        self.confidence_threshold = confidence_threshold
        self.model = None
        self.current_frame = None
        self.detected_persons = []
        
        logger.info(f"Initializing PedestrianDetector with model: {model_path}")
        self._load_model()
    
    def _load_model(self):
        """Load the YOLO model"""
        try:
            self.model = YOLO(self.model_path)
            logger.info(f"Successfully loaded YOLO model: {self.model_path}")
        except Exception as e:
            logger.error(f"Failed to load YOLO model: {e}")
            raise
    
    def process_video(self, video_path):
        """Process entire video file for pedestrian detection"""
        logger.info(f"Processing video: {video_path}")
        
        # Reset detections for new video
        self.detected_persons = []
        
        # Open video file
        cap = cv2.VideoCapture(video_path)
        
        # Check if video opened successfully
        if not cap.isOpened():
            logger.error(f"Could not open video file {video_path}")
            return False
        
        frame_count = 0
        
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    logger.info("End of video or failed to read frame")
                    break
                
                frame_count += 1
                frame_detections = self.detect_pedestrians_in_frame(frame)
                self.detected_persons.append(frame_detections)
                
                # Log progress every 30 frames
                if frame_count % 30 == 0:
                    logger.info(f"Processed {frame_count} frames")
        
        except Exception as e:
            logger.error(f"Error processing video: {e}")
            return False
        finally:
            cap.release()
        
        logger.info(f"Video processing completed. Total frames processed: {len(self.detected_persons)}")
        return True
    
    def detect_pedestrians_in_frame(self, frame):
        """Detect pedestrians in a single frame"""
        if self.model is None:
            logger.error("Model not loaded")
            return []
        
        try:
            # Run inference with verbose disabled
            results = self.model(frame, verbose=False)
            
            # Start with original frame
            annotated_frame = frame.copy()
            self.current_frame = annotated_frame
            
            # Prepare new list for current frame detections
            frame_persons = []
            
            # Draw bounding boxes only for 'person' class
            for box in results[0].boxes:
                cls_id = int(box.cls[0])
                conf = float(box.conf[0])
                
                if self.model.names[cls_id] == "person" and conf > self.confidence_threshold:
                    # Extract bbox coordinates
                    xyxy = box.xyxy[0].cpu().numpy()
                    x1, y1, x2, y2 = map(int, xyxy)
                    
                    # Store coordinates in list
                    person_coords = [x1, y1, x2, y2]
                    frame_persons.append(person_coords)
                    
                    # Draw bounding box
                    cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    
                    # Draw label with confidence
                    label = f"person {conf:.2f}"
                    cv2.putText(annotated_frame, label, (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            
            if frame_persons:
                logger.debug(f"Detected persons in frame: {frame_persons}")
            
            return frame_persons
            
        except Exception as e:
            logger.error(f"Error detecting pedestrians in frame: {e}")
            return []
    
    def get_detection_count(self):
        """Get total number of frames processed"""
        return len(self.detected_persons)
    
    def get_current_frame(self):
        """Get the current annotated frame"""
        return self.current_frame
    
    def save_current_frame(self, output_path):
        """Save the current annotated frame to file"""
        if self.current_frame is not None:
            try:
                cv2.imwrite(output_path, self.current_frame)
                logger.info(f"Saved current frame to: {output_path}")
                return True
            except Exception as e:
                logger.error(f"Failed to save frame: {e}")
                return False
        else:
            logger.warning("No current frame to save")
            return False

class PedestrianDetectionWorker:
    def __init__(self):
        self.running = True
        self.cycle_time = 1.0  # seconds between cycles
        self.detector = None
        self.video_path = "ped_det_1.avi"  # Default video path
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
        logger.info("Initializing PedestrianDetection worker")
        
        try:
            # Initialize the pedestrian detector
            self.detector = PedestrianDetector(model_path="yolo11n.pt", confidence_threshold=0.7)
            logger.info("PedestrianDetection worker initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize detector: {e}")
            raise
    
    def process_cycle(self):
        """Main processing cycle - implement your worker logic here"""
        try:
            if self.detector is None:
                logger.error("Detector not initialized")
                return
            
            logger.info("Processing pedestrian detection cycle")
            
            # Process the video for pedestrian detection
            success = self.detector.process_video(self.video_path)
            
            if success:
                detection_count = self.detector.get_detection_count()
                logger.info(f"Successfully processed video. Total frames: {detection_count}")
                
                # Optional: Save the last processed frame
                # self.detector.save_current_frame("output_frame.jpg")
            else:
                logger.error("Failed to process video")
            
        except Exception as e:
            logger.error(f"Error in processing cycle: {e}")
    
    def cleanup(self):
        """Cleanup resources before shutdown"""
        logger.info("Cleaning up PedestrianDetection worker")
        
        # Clean up detector resources
        if self.detector:
            self.detector = None
            logger.info("Detector resources cleaned up")
        
    def run(self):
        """Main worker loop"""
        try:
            self.initialize()
            
            logger.info("Starting PedestrianDetection worker main loop")
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
            logger.info("PedestrianDetection worker stopped")

if __name__ == '__main__':
    worker = PedestrianDetectionWorker()
    worker.run()
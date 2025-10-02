import cv2
import numpy as np
import threading
import time
from collections import deque
from datetime import datetime
import os
from .network_interface import receive_frame_from_network, receive_collision_sensor_data


class AccidentRecorder:
    def __init__(self, fps=30, frame_width=640, frame_height=360, save_directory="accident_recordings"):
        """
        Initialize the Accident Recorder system.
        
        Args:
            fps (int): Default/initial frames per second for recording (will be adjusted dynamically)
            frame_width (int): Width of the frames
            frame_height (int): Height of the frames
            save_directory (str): Directory to save accident recordings
        """
        self.default_fps = fps
        self.actual_fps = fps  # Will be calculated dynamically
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.save_directory = save_directory
        
        # Frame timing tracking for dynamic FPS calculation
        self.frame_timestamps = deque(maxlen=100)  # Keep last 100 frame timestamps
        self.last_frame_time = None
        self.fps_calculation_window = 30  # Number of frames to use for FPS calculation
        
        # Buffer for continuous 15-second recording
        self.buffer_duration = 15  # seconds
        self.max_buffer_frames = self.default_fps * self.buffer_duration  # Initial estimate
        self.frame_buffer = deque(maxlen=self.max_buffer_frames)
        
        # Accident recording state
        self.is_recording_accident = False
        self.accident_start_time = None
        self.accident_frames = []
        self.accident_duration = 30  # seconds total (15 before + 15 after collision)
        
        # Threading locks for thread safety
        self.buffer_lock = threading.Lock()
        self.recording_lock = threading.Lock()
        
        # Create save directory if it doesn't exist
        os.makedirs(self.save_directory, exist_ok=True)

    def _calculate_actual_fps(self):
        """
        Calculate actual FPS based on recent frame arrival times.
        
        Returns:
            float: Calculated FPS based on frame timing
        """
        if len(self.frame_timestamps) < 2:
            return self.default_fps
        
        # Use recent frames for calculation (up to fps_calculation_window)
        recent_timestamps = list(self.frame_timestamps)[-self.fps_calculation_window:]
        
        if len(recent_timestamps) < 2:
            return self.default_fps
        
        # Calculate time differences between consecutive frames
        time_diffs = []
        for i in range(1, len(recent_timestamps)):
            diff = (recent_timestamps[i] - recent_timestamps[i-1]).total_seconds()
            if diff > 0:  # Avoid division by zero
                time_diffs.append(diff)
        
        if not time_diffs:
            return self.default_fps
        
        # Calculate average time between frames
        avg_frame_interval = sum(time_diffs) / len(time_diffs)
        
        # Calculate FPS (frames per second)
        calculated_fps = 1.0 / avg_frame_interval if avg_frame_interval > 0 else self.default_fps
        
        # Smooth the FPS change to avoid sudden jumps
        self.actual_fps = 0.8 * self.actual_fps + 0.2 * calculated_fps
        
        return self.actual_fps

    def _update_buffer_size(self):
        """
        Update buffer size based on current actual FPS to maintain 15-second duration.
        """
        new_max_frames = int(self.actual_fps * self.buffer_duration)
        
        # Only update if there's a significant change
        if abs(new_max_frames - self.frame_buffer.maxlen) > 5:
            # Create new deque with updated size, preserving existing frames
            old_frames = list(self.frame_buffer)
            self.frame_buffer = deque(old_frames, maxlen=new_max_frames)

    def add_frame_to_buffer(self, frame):
        """
        Add a frame to the continuous recording buffer.
        
        Args:
            frame (np.ndarray): Frame to add to buffer
        """
        if frame is None:
            return
        
        current_time = datetime.now()
        
        # Track frame timing for FPS calculation
        self.frame_timestamps.append(current_time)
        self.last_frame_time = current_time
        
        # Calculate actual FPS based on frame arrival
        self._calculate_actual_fps()
        
        # Update buffer size if needed
        self._update_buffer_size()
            
        with self.buffer_lock:
            # Add timestamp to frame metadata
            frame_data = {
                'frame': frame.copy(),
                'timestamp': current_time
            }
            self.frame_buffer.append(frame_data)

    def collision_detected(self, collision_data=None):
        """
        Handler called when collision is detected.
        Starts accident recording process.
        
        Args:
            collision_data (dict): Optional collision information
        """
        with self.recording_lock:
            if self.is_recording_accident:
                return
                
            self.is_recording_accident = True
            self.accident_start_time = datetime.now()
            
            # Copy current buffer (15 seconds before collision)
            with self.buffer_lock:
                self.accident_frames = list(self.frame_buffer)
            
            # Start thread to continue recording for additional 15 seconds
            recording_thread = threading.Thread(target=self._continue_accident_recording)
            recording_thread.daemon = True
            recording_thread.start()

    def _continue_accident_recording(self):
        """
        Continue recording for additional 15 seconds after collision detection.
        This runs in a separate thread.
        """
        start_time = datetime.now()
        recording_duration = 15  # seconds
        
        while self.is_recording_accident:
            current_time = datetime.now()
            elapsed_time = (current_time - start_time).total_seconds()
            
            # Check if we've recorded for the required duration
            if elapsed_time >= recording_duration:
                break
            
            # Get frame from network
            frame = receive_frame_from_network()
            
            if frame is not None:
                frame_data = {
                    'frame': frame.copy(),
                    'timestamp': current_time
                }
                self.accident_frames.append(frame_data)
            
            # No artificial delay - just process frames as they arrive
            # Add delay managed by user set fps
            time.sleep(1.0 / self.default_fps)
        
        # Save the accident recording
        self._save_accident_recording()
        
        # Reset recording state
        with self.recording_lock:
            self.is_recording_accident = False
            self.accident_start_time = None
            self.accident_frames = []

    def _save_accident_recording(self):
        """
        Save the accident recording to a video file using actual frame timing.
        """
        if not self.accident_frames:
            return
        
        # Calculate the actual FPS based on the recorded frames
        if len(self.accident_frames) > 1:
            first_frame_time = self.accident_frames[0]['timestamp']
            last_frame_time = self.accident_frames[-1]['timestamp']
            total_duration = (last_frame_time - first_frame_time).total_seconds()
            
            if total_duration > 0:
                recording_fps = (len(self.accident_frames) - 1) / total_duration
            else:
                recording_fps = self.actual_fps
        else:
            recording_fps = self.actual_fps
        
        # Generate filename with timestamp
        timestamp_str = self.accident_start_time.strftime("%Y%m%d_%H%M%S")
        filename = f"accident_{timestamp_str}.avi"
        filepath = os.path.join(self.save_directory, filename)
        
        # Define codec and create VideoWriter with calculated FPS
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        out = cv2.VideoWriter(filepath, fourcc, recording_fps, (self.frame_width, self.frame_height))
        
        try:
            for frame_data in self.accident_frames:
                frame = frame_data['frame']
                
                # Resize frame if necessary
                if frame.shape[:2] != (self.frame_height, self.frame_width):
                    frame = cv2.resize(frame, (self.frame_width, self.frame_height))
                
                # Ensure frame is in BGR format for video writing
                if len(frame.shape) == 3 and frame.shape[2] == 3:
                    # Assume it's already BGR
                    out.write(frame)
                elif len(frame.shape) == 2:
                    # Grayscale - convert to BGR
                    frame_bgr = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
                    out.write(frame_bgr)
            
            # Calculate actual recording duration
            if len(self.accident_frames) > 1:
                first_time = self.accident_frames[0]['timestamp']
                last_time = self.accident_frames[-1]['timestamp']
                actual_duration = (last_time - first_time).total_seconds()
            else:
                actual_duration = 0
            
        except Exception as e:
            pass
        finally:
            out.release()

    def run(self):
        """
        Single iteration of recording processing.
        This should be called repeatedly from an external loop.
        
        Returns:
            bool: True if processing was successful, False if an error occurred
        """
        try:
            # Receive frame from network
            frame = receive_frame_from_network()
            
            if frame is not None:
                # Add frame to buffer (this will track timing and calculate FPS)
                self.add_frame_to_buffer(frame)
                
                # Check for collision sensor data
                sensor_data = receive_collision_sensor_data()
                
                if sensor_data and sensor_data.get('collision_detected', False):
                    self.collision_detected(sensor_data)
            else:
                # Small delay only when no frame is available to avoid busy waiting
                time.sleep(0.001)  # 1ms delay
            
            return True
            
        except Exception as e:
            return False

    def get_status(self):
        """
        Get current status of the recorder.
        
        Returns:
            dict: Status information
        """
        with self.buffer_lock:
            buffer_size = len(self.frame_buffer)
        
        with self.recording_lock:
            recording_status = self.is_recording_accident
        
        return {
            'buffer_frames': buffer_size,
            'buffer_duration_seconds': buffer_size / self.actual_fps if self.actual_fps > 0 else 0,
            'is_recording_accident': recording_status,
            'actual_fps': round(self.actual_fps, 2),
            'default_fps': self.default_fps,
            'frame_timestamps_count': len(self.frame_timestamps)
        }
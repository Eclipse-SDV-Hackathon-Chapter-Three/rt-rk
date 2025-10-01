from src.accident_recorder import AccidentRecorder

def main():
    """
    Main application entry point for the Accident Recorder system.
    """
    # Initialize recorder with desired parameters
    recorder = AccidentRecorder(
        fps=30,
        frame_width=640,
        frame_height=360,
        save_directory="accident_recordings"
    )
    
    # Connect to network sources (when available)
    # recorder.connect_to_network(
    #     frame_source_address="192.168.1.100:8080",  # LA system address
    #     sensor_source_address="192.168.1.101:8081"  # ES system address
    # )
    
    try:
        # Start continuous recording
        # This will run indefinitely until interrupted
        recorder.start_continuous_recording()
    except KeyboardInterrupt:
        # recorder.disconnect_from_network()
        pass
    except Exception as e:
        pass

if __name__ == "__main__":
    main()

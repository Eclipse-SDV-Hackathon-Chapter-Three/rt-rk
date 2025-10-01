//! # ucar_core
//!
//! Core library for uCar sensor integration with uProtocol.
//! This crate provides sensor data structures and utilities for CARLA integration.

use serde::{Deserialize, Serialize};

// Re-export sensor types for convenience
pub use ego_vehicle::sensors::*;
pub use ego_vehicle::helpers::*;

/// Extended sensor data structure that combines CARLA sensor data with uProtocol metadata
#[derive(Serialize, Deserialize, Debug, Clone)]
pub struct UCarSensorData {
    /// Sensor identifier
    pub sensor_id: String,
    /// Timestamp when the data was captured
    pub timestamp: u64,
    /// Sensor type identifier
    pub sensor_type: String,
    /// Raw sensor data (JSON serialized)
    pub data: serde_json::Value,
    /// uProtocol message metadata
    pub metadata: SensorMetadata,
}

/// Metadata for uProtocol sensor messages
#[derive(Serialize, Deserialize, Debug, Clone)]
pub struct SensorMetadata {
    /// Source authority
    pub authority: String,
    /// Entity ID
    pub entity_id: u32,
    /// Resource ID
    pub resource_id: u16,
    /// Message sequence number
    pub sequence: u64,
}

impl SensorMetadata {
    /// Create new sensor metadata with default uCar settings
    pub fn new_ucar(resource_id: u16, sequence: u64) -> Self {
        Self {
            authority: "ucar".to_string(),
            entity_id: 0x00010001,
            resource_id,
            sequence,
        }
    }
}

/// Sensor type constants for uCar
pub mod sensor_types {
    pub const IMAGE: &str = "image";
    pub const LIDAR: &str = "lidar";
    pub const RADAR: &str = "radar";
    pub const IMU: &str = "imu";
    pub const COLLISION: &str = "collision";
    pub const LANE_INVASION: &str = "lane_invasion";
    pub const OBSTACLE_DETECTION: &str = "obstacle_detection";
}

/// Resource ID constants for different sensor types
pub mod resource_ids {
    pub const IMAGE: u16 = 0x1000;
    pub const LIDAR: u16 = 0x1001;
    pub const RADAR: u16 = 0x1002;
    pub const IMU: u16 = 0x1003;
    pub const COLLISION: u16 = 0x1004;
    pub const LANE_INVASION: u16 = 0x1005;
    pub const OBSTACLE_DETECTION: u16 = 0x1006;
}

/// Utility functions for sensor data processing
pub mod utils {
    use super::*;
    use std::time::{SystemTime, UNIX_EPOCH};

    /// Create UCarSensorData from CARLA image sensor data
    pub fn create_image_sensor_data(
        sensor_id: String,
        image_data: &serde_json::Value,
        sequence: u64,
    ) -> UCarSensorData {
        UCarSensorData {
            sensor_id,
            timestamp: SystemTime::now()
                .duration_since(UNIX_EPOCH)
                .unwrap_or_default()
                .as_secs(),
            sensor_type: sensor_types::IMAGE.to_string(),
            data: image_data.clone(),
            metadata: SensorMetadata::new_ucar(resource_ids::IMAGE, sequence),
        }
    }

    /// Create UCarSensorData from CARLA lidar sensor data
    pub fn create_lidar_sensor_data(
        sensor_id: String,
        lidar_data: &serde_json::Value,
        sequence: u64,
    ) -> UCarSensorData {
        UCarSensorData {
            sensor_id,
            timestamp: SystemTime::now()
                .duration_since(UNIX_EPOCH)
                .unwrap_or_default()
                .as_secs(),
            sensor_type: sensor_types::LIDAR.to_string(),
            data: lidar_data.clone(),
            metadata: SensorMetadata::new_ucar(resource_ids::LIDAR, sequence),
        }
    }

    /// Validate sensor data
    pub fn validate_sensor_data(data: &UCarSensorData) -> Result<(), String> {
        if data.sensor_id.is_empty() {
            return Err("Sensor ID cannot be empty".to_string());
        }
        if data.sensor_type.is_empty() {
            return Err("Sensor type cannot be empty".to_string());
        }
        if data.timestamp == 0 {
            return Err("Timestamp cannot be zero".to_string());
        }
        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_sensor_metadata_creation() {
        let metadata = SensorMetadata::new_ucar(resource_ids::IMAGE, 42);
        assert_eq!(metadata.authority, "ucar");
        assert_eq!(metadata.entity_id, 0x00010001);
        assert_eq!(metadata.resource_id, resource_ids::IMAGE);
        assert_eq!(metadata.sequence, 42);
    }

    #[test]
    fn test_image_sensor_data_creation() {
        let image_data = serde_json::json!({
            "width": 800,
            "height": 600,
            "format": "RGB"
        });
        
        let sensor_data = utils::create_image_sensor_data(
            "camera_front".to_string(),
            &image_data,
            1,
        );
        
        assert_eq!(sensor_data.sensor_id, "camera_front");
        assert_eq!(sensor_data.sensor_type, sensor_types::IMAGE);
        assert_eq!(sensor_data.metadata.resource_id, resource_ids::IMAGE);
        assert_eq!(sensor_data.metadata.sequence, 1);
    }

    #[test]
    fn test_sensor_data_validation() {
        let valid_data = UCarSensorData {
            sensor_id: "test_sensor".to_string(),
            timestamp: 1234567890,
            sensor_type: sensor_types::IMAGE.to_string(),
            data: serde_json::json!({}),
            metadata: SensorMetadata::new_ucar(resource_ids::IMAGE, 1),
        };
        
        assert!(utils::validate_sensor_data(&valid_data).is_ok());
        
        let invalid_data = UCarSensorData {
            sensor_id: "".to_string(),
            timestamp: 1234567890,
            sensor_type: sensor_types::IMAGE.to_string(),
            data: serde_json::json!({}),
            metadata: SensorMetadata::new_ucar(resource_ids::IMAGE, 1),
        };
        
        assert!(utils::validate_sensor_data(&invalid_data).is_err());
    }
}

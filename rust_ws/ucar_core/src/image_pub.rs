// use ego_vehicle::sensors::Image;
use carla::client::{ActorBase, Client};
use carla::sensor::data::{
    CollisionEvent, Image as ImageEvent, ImuMeasurement as ImuMeasurementEvent, LaneInvasionEvent,
    LidarMeasurement as LidarMeasurementEvent, ObstacleDetectionEvent,
    RadarMeasurement as RadarMeasurementEvent,
};
use carla_data_serde::{
    CollisionEventSerDe, ImageEventSerBorrowed, ImuMeasurementSerDe, LaneInvasionEventSerDe,
    LidarMeasurementSerBorrowed, ObstacleDetectionEventSerDe, RadarMeasurementSerBorrowed,
};

use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::{Arc, Mutex};
use std::time::Duration;

use up_rust::{
    LocalUriProvider, StaticUriProvider, UListener, UMessage, UMessageBuilder, UPayloadFormat,
    UTransport, UUri,
};
use up_transport_zenoh::UPTransportZenoh;
use up_transport_zenoh::zenoh_config;
use zenoh::{Config, key_expr::KeyExpr};
use ego_vehicle::helpers::setup_sensor_with_transport;
use ego_vehicle::sensors::{
    CollisionFactory, ImageFactory, ImuMeasurementFactory, LaneInvasionFactory,
    LidarMeasurementFactory, ObstacleDetectionFactory, RadarMeasurementFactory,
};

// General constants
const CLIENT_TIME_MS: u64 = 5_000;
const POLLING_EGO_MS: u64 = 1_000;
const WAITING_PUB_MS: u64 = 1;
// Vehicle control constants
const MIN_THROTTLE: f32 = 0.0;
const MIN_STEERING: f32 = -1.0;
const MIN_BRAKING: f32 = 0.0;
const MID_STEERING: f32 = 0.0;
const MAX_THROTTLE: f32 = 1.0;
const MAX_STEERING: f32 = 1.0;
const MAX_BRAKING: f32 = 1.0;

// uProtocol resource IDs
const RESOURCE_VELOCITY_STATUS: u16 = 0x8001;
const RESOURCE_CLOCK_STATUS: u16 = 0x8002;
// uProtocol resource IDs for sensors
const RESOURCE_LANE_INVASION_SENSOR: u16 = 0x8010;
const RESOURCE_COLLISION_SENSOR: u16 = 0x8011;
const RESOURCE_OBSTACLE_DETECTION_SENSOR: u16 = 0x8012;
const RESOURCE_IMAGE_SENSOR: u16 = 0x8013;
const RESOURCE_RADAR_SENSOR: u16 = 0x8014;
const RESOURCE_LIDAR_SENSOR: u16 = 0x8015;
const RESOURCE_IMU_SENSOR: u16 = 0x8016;


// Helper function to create a Zenoh configuration
pub(crate) fn get_zenoh_config() -> zenoh_config::Config {

    let zenoh_string = r#"{
            mode: 'peer',
            scouting: {
                multicast: {
                    enabled: true
                }
            }
        }"#.to_string();

    let zenoh_config = Config::from_json5(&zenoh_string).expect("Failed to load Zenoh config");

    zenoh_config
}


#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    println!("Starting image publisher...");
    // Initiate logging
    pretty_env_logger::init();

    // Stop the program gracefully on Ctrl-C
    let running = Arc::new(AtomicBool::new(true));
    let running_clone = running.clone();

    ctrlc::set_handler(move || {
        log::warn!("Cancelled by user. Bye!");
        running_clone.store(false, Ordering::SeqCst);
    })
    .expect("Error setting Ctrl-C handler");

    let host = "127.0.0.1".to_string();
    let port = 2000;

    let mut carla_client = Client::connect(&host, port, None);

    carla_client.set_timeout(Duration::from_millis(CLIENT_TIME_MS));

    // Configure Carla's World
    let mut carla_world = carla_client.world();
    let mut carla_settings = carla_world.settings();

    carla_settings.synchronous_mode = false;
    carla_settings.fixed_delta_seconds = Some(0.100);

    carla_world.apply_settings(&carla_settings, Duration::from_millis(CLIENT_TIME_MS));


    log::info!(
        "World Settings: Synchronous mode: {}, Fixed delta seconds: {:?}",
        carla_settings.synchronous_mode,
        carla_settings.fixed_delta_seconds
    );

    // // Wait for the Ego Vehicle actor
    // let mut ego_vehicle_id: Option<u32> = None;

    // while running.load(Ordering::SeqCst) && ego_vehicle_id.is_none() {
    //     log::info!("Waiting for the Ego Vehicle actor...");

    //     // Syncronize Carla's world
    //     let _ = carla_world.wait_for_tick();

    //     // Check if the Ego Vehicle actor exists in the world
    //     for actor in carla_world.actors().iter() {
    //         for attribute in actor.attributes().iter() {
    //             if attribute.id() == "role_name"
    //                 && attribute.value_string() == "ego_vehicle_role" // TODO (Sachin): Make this configurable
    //             {
    //                 log::info!(
    //                     "Found '{}' actor with id: {}",
    //                     "ego_vehicle_role".to_string(),
    //                     actor.id()
    //                 );
    //                 ego_vehicle_id = Some(actor.id());
    //                 break;
    //             }
    //         }
    //     }

    //     // Sleep to avoid busy-waiting
    //     tokio::time::sleep(Duration::from_millis(POLLING_EGO_MS)).await;
    // }

    // Wait for the Ego Vehicle actor
    let mut ego_vehicle_id: Option<u32> = None;

    while running.load(Ordering::SeqCst) && ego_vehicle_id.is_none() {
        log::info!("Waiting for the Ego Vehicle actor...");

        // Syncronize Carla's world
        let _ = carla_world.wait_for_tick();

        // Check if the Ego Vehicle actor exists in the world
        let actors = carla_world.actors();
        for actor in actors.iter() {
            // Add safety check and error handling
            match std::panic::catch_unwind(|| {
                let attributes = actor.attributes();
                for attribute in attributes.iter() {
                    if attribute.id() == "role_name" {
                        let value = attribute.value_string();
                        if value == "ego_vehicle_role" {
                            log::info!(
                                "Found '{}' actor with id: {}",
                                "ego_vehicle_role",
                                actor.id()
                            );
                            return Some(actor.id());
                        }
                    }
                }
                None
            }) {
                Ok(Some(id)) => {
                    ego_vehicle_id = Some(id);
                    break;
                }
                Ok(None) => continue,
                Err(_) => {
                    log::warn!("Error accessing actor attributes, skipping actor");
                    continue;
                }
            }
        }

        // Sleep to avoid busy-waiting
        tokio::time::sleep(Duration::from_millis(POLLING_EGO_MS)).await;
    }

    // Check if we found the ego vehicle before proceeding
    if ego_vehicle_id.is_none() {
        log::error!("Could not find ego vehicle actor. Exiting.");
        return Err("Ego vehicle not found".into());
    }


    // Initialize uProtocol logging
    UPTransportZenoh::try_init_log_from_env();

    // Create a uProtocol URI provider for this vehicle
    // This defines the identity of this node in the uProtocol network
    let uri_provider = StaticUriProvider::new("egovehicle", 0, 2);

    // Create the uProtocol transport using Zenoh as the underlying transport
    let transport: Arc<dyn UTransport> = Arc::new(
        UPTransportZenoh::builder(uri_provider.get_authority())
            .expect("invalid authority name")
            .with_config(get_zenoh_config())
            .build()
            .await?,
    );

    // -- Set up Sensor for Image -- (generic)
    // let (_image_comms, _ego_vehicle_sensor_image_id, _image_sensor_keepalive) =
    //     if let Some(ego_vehicle_sensor_image_role) = args.ego_vehicle_sensor_image_role {
    //         let uuri = uri_provider.get_resource_uri(RESOURCE_IMAGE_SENSOR);

    //         // Encoder: ImageEvent -> Vec<u8> (borrow-only)
    //         let encode = |evt: ImageEvent| {
    //             // Borrow the event so the payload can serialize without copying the image buffer
    //             let serde_evt: ImageEventSerBorrowed<'_> = (&evt).into();
    //             serde_json::to_vec(&serde_evt)
    //                 .map_err(|e| -> Box<dyn std::error::Error + Send + Sync> { Box::new(e) })
    //         };

    //         let (_image_comms, image_actor_id, _image_sensor_keepalive) =
    //             setup_sensor_with_transport(
    //                 &carla_world,
    //                 &running,
    //                 &ego_vehicle_sensor_image_role,
    //                 "image_sensor",
    //                 POLLING_EGO_MS,
    //                 ImageFactory,
    //                 uuri,
    //                 encode,
    //                 UPayloadFormat::UPAYLOAD_FORMAT_JSON,
    //                 Arc::clone(&transport),
    //             )
    //             .await
    //             .expect("Unable to set up obstacle detection sensor with transport");

    //         let _ego_vehicle_sensor_image_id = Some(image_actor_id);

    //         (
    //             Some(_image_comms),
    //             Some(_ego_vehicle_sensor_image_id),
    //             Some(_image_sensor_keepalive),
    //         )
    //     } else {
    //         (None, None, None)
    //     };


    // -- Set up Sensor for Image -- (generic)
    let (_image_comms, _ego_vehicle_sensor_image_id, _image_sensor_keepalive) = {
        let ego_vehicle_sensor_image_role = "ego_vehicle_role";
        let uuri = uri_provider.get_resource_uri(RESOURCE_IMAGE_SENSOR);

        // Encoder: ImageEvent -> Vec<u8> (borrow-only)
        let encode = |evt: ImageEvent| {
            // Borrow the event so the payload can serialize without copying the image buffer
            let serde_evt: ImageEventSerBorrowed<'_> = (&evt).into();
            serde_json::to_vec(&serde_evt)
                .map_err(|e| -> Box<dyn std::error::Error + Send + Sync> { Box::new(e) })
        };

        let (_image_comms, image_actor_id, _image_sensor_keepalive) =
            setup_sensor_with_transport(
                &carla_world,
                &running,
                &ego_vehicle_sensor_image_role,
                "image_sensor",
                POLLING_EGO_MS,
                ImageFactory,
                uuri,
                encode,
                UPayloadFormat::UPAYLOAD_FORMAT_JSON,
                Arc::clone(&transport),
            )
            .await
            .expect("Unable to set up image sensor with transport");

        let _ego_vehicle_sensor_image_id = Some(image_actor_id);

        (
            Some(_image_comms),
            Some(_ego_vehicle_sensor_image_id),
            Some(_image_sensor_keepalive),
        )
    };


    Ok(())
}
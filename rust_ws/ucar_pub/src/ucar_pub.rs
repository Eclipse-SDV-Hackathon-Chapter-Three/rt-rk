use std::thread;
use std::time::Duration;
use up_rust::{UMessageBuilder, UPayloadFormat, UTransport, UUri};
use up_transport_zenoh::{UPTransportZenoh, zenoh_config};
use zenoh::Config;
use log;
use serde::{Deserialize, Serialize};

// Simple message structure for "Hello World"
#[derive(Serialize, Deserialize, Debug)]
struct HelloMessage {
    message: String,
    timestamp: u64,
    counter: u32,
}

// Helper function to create a Zenoh configuration (based on ego-vehicle-sensor-publisher.rs)
fn get_zenoh_config() -> zenoh_config::Config {
    // Use peer mode but enable multicast scouting for discovery
    let zenoh_string = r#"{
        mode: 'peer',
        scouting: {
            multicast: {
                enabled: true
            }
        }
    }"#;

    Config::from_json5(zenoh_string).expect("Failed to load Zenoh config")
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    // Initialize logger (same as ego-vehicle-sensor-publisher.rs)
    env_logger::Builder::from_env(
        env_logger::Env::default().default_filter_or("info")
    ).init();

    log::info!("🚀 Starting ucar_pub Hello World publisher using uProtocol...");

    // Create transport (following the pattern from ego-vehicle-sensor-publisher.rs)
    let transport = UPTransportZenoh::builder("ucar")
        .expect("authority not accepted!")
        .with_config(get_zenoh_config())
        .build()
        .await
        .expect("unable to build UPTransportZenoh");

    log::info!("✅ uProtocol transport initialized successfully");

    // Create UUri for our hello world topic (following uProtocol specification)
    let uuri = UUri::try_from_parts(
        "ucar",           // authority (matching our transport)
        0x00010001,       // ue_id (entity ID)
        1,                // ue_version_major (using u8 value)
        0x8000,           // resource_id (using u16 value)
    ).expect("Failed to create UUri");

    log::info!("📍 Publishing to UUri: {:?}", uuri);

    let mut counter = 0u32;

    loop {
        counter += 1;
        
        // Create hello world message
        let hello_msg = HelloMessage {
            message: format!("Hello World from ucar_pub! Message #{}", counter),
            timestamp: std::time::SystemTime::now()
                .duration_since(std::time::UNIX_EPOCH)
                .unwrap()
                .as_secs(),
            counter,
        };

        log::info!("📝 Publishing message: {:?}", hello_msg);

        // Serialize the message (following the pattern from ego-vehicle-sensor-publisher.rs)
        let payload_ser = serde_json::to_vec(&hello_msg)
            .expect("Unable to serialize hello world message");

        // Create UMessage (using the same pattern as ego-vehicle-sensor-publisher.rs)
        let umsg = UMessageBuilder::publish(uuri.clone())
            .build_with_payload(payload_ser, UPayloadFormat::UPAYLOAD_FORMAT_JSON)
            .expect("Unable to create publish message");

        // Send the message (same as ego-vehicle-sensor-publisher.rs)
        match transport.send(umsg).await {
            Ok(_) => {
                log::info!("✅ Successfully sent hello world message #{}", counter);
                println!("📡 Sent: \"{}\"", hello_msg.message);
            }
            Err(e) => {
                log::error!("❌ Failed to send message: {:?}", e);
                eprintln!("❌ Failed to send message #{}: {:?}", counter, e);
            }
        }

        // Wait 2 seconds before sending next message
        thread::sleep(Duration::from_secs(2));
    }
}

use std::sync::Arc;
use std::thread;
use core::pin::Pin;
use std::future::Future;
use up_rust::{UListener, UMessage, UTransport, UUri};
use up_transport_zenoh::{UPTransportZenoh, zenoh_config};
use zenoh::Config;
use log;
use serde::{Deserialize, Serialize};

// Same message structure as our publisher
#[derive(Serialize, Deserialize, Debug)]
struct HelloMessage {
    message: String,
    timestamp: u64,
    counter: u32,
}

// Helper function to create a Zenoh configuration (same as publisher)
fn get_zenoh_config() -> zenoh_config::Config {
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

// Listener for Hello World messages
struct HelloWorldListener;

impl UListener for HelloWorldListener {
    fn on_receive<'life0, 'async_trait>(
        &'life0 self,
        msg: UMessage,
    ) -> Pin<Box<dyn Future<Output = ()> + Send + 'async_trait>>
    where
        Self: 'async_trait,
        'life0: 'async_trait,
    {
        Box::pin(async move {
            let Some(bytes) = msg.payload.as_deref() else {
                log::warn!("Received message with no payload");
                return;
            };
            
            if bytes.is_empty() {
                log::warn!("Received message with empty payload");
                return;
            }

            match serde_json::from_slice::<HelloMessage>(bytes) {
                Ok(hello_msg) => {
                    log::info!("📨 Received Hello Message: {:?}", hello_msg);
                    println!("📨 Received: \"{}\" (#{}) at timestamp {}", 
                            hello_msg.message, 
                            hello_msg.counter, 
                            hello_msg.timestamp);
                }
                Err(err) => {
                    log::error!("❌ Failed to deserialize Hello World message: {:?}", err);
                    eprintln!("❌ Failed to deserialize message: {:?}", err);
                }
            }
        })
    }
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    // Initialize logger (same as publisher)
    env_logger::Builder::from_env(
        env_logger::Env::default().default_filter_or("info")
    ).init();

    log::info!("🚀 Starting ucar_sub Hello World subscriber using uProtocol...");

    // Create transport (same authority as publisher for communication)
    let transport = UPTransportZenoh::builder("ucar")
        .expect("authority not accepted!")
        .with_config(get_zenoh_config())
        .build()
        .await
        .expect("unable to build UPTransportZenoh");

    log::info!("✅ uProtocol transport initialized successfully");

    // Create the same UUri that the publisher uses
    let uuri = UUri::try_from_parts(
        "ucar",           // authority (matching our publisher)
        0x00010001,       // ue_id (entity ID)
        1,                // ue_version_major
        0x8000,           // resource_id
    ).expect("Failed to create UUri");

    log::info!("📍 Subscribing to UUri: {:?}", uuri);

    // Create listener for Hello World messages
    let hello_listener: Arc<dyn UListener> = Arc::new(HelloWorldListener);

    // Register listener to receive messages
    transport
        .register_listener(&uuri, None, hello_listener)
        .await
        .expect("Failed to register listener for Hello World messages");

    log::info!("👂 Listening for Hello World messages...");
    println!("👂 Listening for Hello World messages from ucar_pub...");
    println!("Press Ctrl+C to stop");

    // Keep the subscriber running
    thread::park();

    Ok(())
}
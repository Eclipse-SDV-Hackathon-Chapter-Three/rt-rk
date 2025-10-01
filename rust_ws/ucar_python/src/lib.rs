use std::sync::Arc;
use std::sync::Mutex;
use std::thread;
use core::pin::Pin;
use std::future::Future;
use pyo3::prelude::*;
use up_rust::{UListener, UMessage, UTransport, UUri};
use up_transport_zenoh::{UPTransportZenoh, zenoh_config};
use zenoh::Config;
use serde::{Deserialize, Serialize};

// Same message structure as the subscriber
#[derive(Serialize, Deserialize, Debug, Clone)]
pub struct HelloMessage {
    pub message: String,
    pub timestamp: u64,
    pub counter: u32,
}

// Convert to Python dict for easy access
impl IntoPy<PyObject> for HelloMessage {
    fn into_py(self, py: Python<'_>) -> PyObject {
        let dict = pyo3::types::PyDict::new(py);
        dict.set_item("message", self.message).unwrap();
        dict.set_item("timestamp", self.timestamp).unwrap();
        dict.set_item("counter", self.counter).unwrap();
        dict.into()
    }
}

// Python callback wrapper
struct PythonListener {
    callback: Arc<Mutex<PyObject>>,
}

impl PythonListener {
    fn new(callback: PyObject) -> Self {
        Self {
            callback: Arc::new(Mutex::new(callback)),
        }
    }
}

impl UListener for PythonListener {
    fn on_receive<'life0, 'async_trait>(
        &'life0 self,
        msg: UMessage,
    ) -> Pin<Box<dyn Future<Output = ()> + Send + 'async_trait>>
    where
        Self: 'async_trait,
        'life0: 'async_trait,
    {
        let callback = self.callback.clone();
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
                    
                    // Call Python callback
                    Python::with_gil(|py| {
                        if let Ok(callback_ref) = callback.lock() {
                            let py_msg = hello_msg.into_py(py);
                            if let Err(e) = callback_ref.call1(py, (py_msg,)) {
                                eprintln!("Error calling Python callback: {:?}", e);
                            }
                        }
                    });
                }
                Err(err) => {
                    log::error!("❌ Failed to deserialize Hello World message: {:?}", err);
                }
            }
        })
    }
}

// Helper function to create a Zenoh configuration
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

#[pyclass]
pub struct UCarSubscriber {
    runtime: Option<Arc<tokio::runtime::Runtime>>,
    transport: Option<Arc<UPTransportZenoh>>,
    uuri: Option<UUri>,
}

#[pymethods]
impl UCarSubscriber {
    #[new]
    fn new() -> PyResult<Self> {
        // Initialize logger
        env_logger::Builder::from_env(
            env_logger::Env::default().default_filter_or("info")
        ).try_init().ok(); // ok() to ignore if already initialized

        // Create tokio runtime
        let runtime = tokio::runtime::Runtime::new()
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!("Failed to create tokio runtime: {:?}", e)))?;

        Ok(Self {
            runtime: Some(Arc::new(runtime)),
            transport: None,
            uuri: None,
        })
    }

    /// Initialize the uProtocol transport
    fn initialize(&mut self) -> PyResult<()> {
        let runtime = self.runtime.as_ref()
            .ok_or_else(|| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("Runtime not available"))?
            .clone();

        let result = runtime.block_on(async {
            log::info!("🚀 Initializing ucar_python subscriber using uProtocol...");

            // Create transport
            let transport = UPTransportZenoh::builder("ucar")
                .map_err(|e| format!("Authority not accepted: {:?}", e))?
                .with_config(get_zenoh_config())
                .build()
                .await
                .map_err(|e| format!("Unable to build UPTransportZenoh: {:?}", e))?;

            log::info!("✅ uProtocol transport initialized successfully");

            // Create UUri for our hello world topic
            let uuri = UUri::try_from_parts(
                "ucar",           // authority
                0x00010001,       // ue_id (entity ID)
                1,                // ue_version_major
                0x8000,           // resource_id
            ).map_err(|e| format!("Failed to create UUri: {:?}", e))?;

            log::info!("📍 Will subscribe to UUri: {:?}", uuri);

            Ok((Arc::new(transport), uuri))
        }).map_err(|e: String| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e))?;

        self.transport = Some(result.0);
        self.uuri = Some(result.1);

        Ok(())
    }

    /// Start listening for messages with a Python callback
    fn start_listening(&self, callback: PyObject) -> PyResult<()> {
        let runtime = self.runtime.as_ref()
            .ok_or_else(|| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("Runtime not available"))?
            .clone();
        
        let transport = self.transport.as_ref()
            .ok_or_else(|| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("Transport not initialized. Call initialize() first."))?
            .clone();
        
        let uuri = self.uuri.as_ref()
            .ok_or_else(|| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("UUri not set. Call initialize() first."))?
            .clone();

        runtime.spawn(async move {
            log::info!("👂 Starting to listen for Hello World messages...");

            // Create Python listener
            let listener: Arc<dyn UListener> = Arc::new(PythonListener::new(callback));

            // Register listener
            match transport.register_listener(&uuri, None, listener).await {
                Ok(_) => log::info!("✅ Successfully registered listener for Hello World messages"),
                Err(e) => log::error!("❌ Failed to register listener: {:?}", e),
            }
        });

        Ok(())
    }

    /// Get connection status
    fn is_initialized(&self) -> bool {
        self.transport.is_some() && self.uuri.is_some()
    }
}

/// ucar_python module - provides Python access to ucar subscriber functionality
#[pymodule]
fn ucar_python(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<UCarSubscriber>()?;
    Ok(())
}
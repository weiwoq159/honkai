use serde::{Deserialize, Serialize};
use serde_json::Value;

use crate::services::python_runner::run_python_plugin;

#[derive(Debug, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct RunToolPayload {
    pub plugin_id: String,
    pub input: Value,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct RunToolResult {
    pub success: bool,
    pub message: String,
    pub data: Option<Value>,
}

#[tauri::command]
pub fn run_tool(window: tauri::Window, payload: RunToolPayload) -> Result<RunToolResult, String> {
    run_python_plugin(window, payload).map_err(|error| error.to_string())
}

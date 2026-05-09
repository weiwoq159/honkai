use serde::{Deserialize, Serialize};
use serde_json::Value;
use tauri::AppHandle;

use crate::services::python_runner::run_python_plugin;

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct RunToolPayload {
    pub plugin_id: String,
    pub input: Value,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct RunToolResult {
    pub success: bool,
    pub message: String,

    #[serde(default)]
    pub data: Option<Value>,

    #[serde(default)]
    pub logs: Vec<String>,
}

#[tauri::command]
pub async fn run_tool(app: AppHandle, payload: RunToolPayload) -> Result<RunToolResult, String> {
    tauri::async_runtime::spawn_blocking(move || run_python_plugin(app, payload))
        .await
        .map_err(|error| error.to_string())?
}

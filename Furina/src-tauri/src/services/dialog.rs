use crate::structs::index::SResponse;
use serde_json::Value;
use tauri::AppHandle;
use tauri_plugin_dialog::{DialogExt, FilePath};

#[tauri::command]
pub async fn open_file_dialog(app: AppHandle) -> Result<SResponse<Value>, String> {
    let file_path = app
        .dialog()
        .file()
        .blocking_pick_folder()
        .ok_or("未选择文件夹")?;
    let folder_path = match file_path {
        FilePath::Path(p) => p.into_os_string(),
        FilePath::Url(_) => return Err("暂不支持 URL 类型路径".into()),
    };
    return Ok(SResponse::success(
        serde_json::json!({"current_page": folder_path.into_string().unwrap()}),
    ));
}

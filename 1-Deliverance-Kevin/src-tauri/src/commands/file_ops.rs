use std::path::PathBuf;

use serde::{Deserialize, Serialize};

#[derive(Debug, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct DeleteFilesPayload {
    pub file_paths: Vec<String>,
}

#[derive(Debug, Serialize)]
#[serde(rename_all = "camelCase")]
pub struct DeleteFileItemResult {
    pub path: String,
    pub success: bool,
    pub message: String,
}

#[derive(Debug, Serialize)]
#[serde(rename_all = "camelCase")]
pub struct DeleteFilesResult {
    pub success: bool,
    pub message: String,
    pub deleted_count: usize,
    pub failed_count: usize,
    pub items: Vec<DeleteFileItemResult>,
}

#[tauri::command]
pub fn move_files_to_trash(payload: DeleteFilesPayload) -> Result<DeleteFilesResult, String> {
    if payload.file_paths.is_empty() {
        return Err("请选择需要删除的文件".to_string());
    }

    let mut items: Vec<DeleteFileItemResult> = Vec::new();

    for file_path in payload.file_paths {
        let path = PathBuf::from(&file_path);

        if !path.exists() {
            items.push(DeleteFileItemResult {
                path: file_path,
                success: false,
                message: "文件不存在".to_string(),
            });
            continue;
        }

        if !path.is_file() {
            items.push(DeleteFileItemResult {
                path: file_path,
                success: false,
                message: "不是有效文件".to_string(),
            });
            continue;
        }

        match trash::delete(&path) {
            Ok(_) => {
                items.push(DeleteFileItemResult {
                    path: file_path,
                    success: true,
                    message: "已移入回收站".to_string(),
                });
            }
            Err(error) => {
                items.push(DeleteFileItemResult {
                    path: file_path,
                    success: false,
                    message: error.to_string(),
                });
            }
        }
    }

    let deleted_count = items.iter().filter(|item| item.success).count();
    let failed_count = items.len() - deleted_count;

    Ok(DeleteFilesResult {
        success: failed_count == 0,
        message: format!(
            "删除完成，成功 {} 个，失败 {} 个",
            deleted_count, failed_count
        ),
        deleted_count,
        failed_count,
        items,
    })
}

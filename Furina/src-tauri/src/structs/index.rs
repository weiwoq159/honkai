use serde::{Deserialize, Serialize};
use sqlx::SqlitePool;
use serde_json::Value;
use sqlx::FromRow;

#[derive(Serialize, Deserialize)]
pub struct SResponse<T> {
    pub status: u16,
    pub message: String,
    pub data: T,
}

impl<T> SResponse<T> {
    // 创建成功响应
    pub fn success(data: T) -> Self {
        SResponse {
            status: 200,
            message: "success".to_string(),
            data,
        }
    }

    // 创建错误响应
    pub fn error(status: u16, message: String) -> SResponse<String> {
        SResponse {
            status,
            message: message.clone(),
            data: message,
        }
    }
}
#[derive(Debug, Clone, serde::Deserialize, sqlx::FromRow, serde::Serialize)]
pub struct MediaItem {
    pub preview_url: String,
    pub url: String,
    pub media_type: Option<String>,
    pub format: Option<String>,
    pub blog_id: Option<String>,
    pub user_id: Option<String>,
    pub created_at: Option<String>,
    pub origin_from: Option<String>,
    pub is_deleted: Option<u8>,
    pub file_name: Option<String>,
    pub md5_code: Option<String>,
    pub download_url: Option<String>
}
pub struct MyState {
    pub pool: SqlitePool,
}
impl MediaItem {
    #[allow(dead_code)]
    fn from_json(item: &Value) -> Result<MediaItem, String> {
        // 通过 `item` 提取数据，构造 MediaItem
        let preview_url = item
            .get("preview_url")
            .and_then(|v| v.as_str())
            .unwrap_or_default()
            .to_string();

        let url = item
            .get("url")
            .and_then(|v| v.as_str())
            .unwrap_or_default()
            .to_string();

        let file_name = item
            .get("file_name")
            .and_then(|v| v.as_str())
            .unwrap_or_default()
            .to_string();


        let download_url = item
            .get("download_url")
            .and_then(|v| v.as_str())
            .unwrap_or_default()
            .to_string();

        let media_type = item
            .get("media_type")
            .and_then(|v| v.as_str())
            .map(|s| s.to_string());

        let format = item
            .get("format")
            .and_then(|v| v.as_str())
            .map(|s| s.to_string());

        let blog_id = item
            .get("blog_id")
            .and_then(|v| v.as_str())
            .map(|s| s.to_string());

        let user_id = item
            .get("user_id")
            .and_then(|v| v.as_str())
            .map(|s| s.to_string());

        let created_at = item
            .get("created_at")
            .and_then(|v| v.as_str())
            .map(|s| s.to_string());

        let origin_from = item
            .get("origin_from")
            .and_then(|v| v.as_str())
            .map(|s| s.to_string());

        let is_deleted = item
            .get("is_deleted")
            .and_then(|v| v.as_u64())
            .map(|v| v as u8);

        let md5_code = item
            .get("md5_code")
            .and_then(|v| v.as_str())
            .map(|s| s.to_string());

        Ok(MediaItem {
            preview_url,
            url,
            media_type,
            format,
            blog_id,
            user_id,
            created_at,
            origin_from,
            is_deleted,
            file_name: Some(file_name),
            md5_code,
            download_url: Some(download_url),
        })
    }
}

use chrono::NaiveDateTime;

#[derive(Debug, Clone, sqlx::Type)]
#[sqlx(rename_all = "lowercase")] // 对应数据库中的小写文本：pending, running 等
pub enum TaskStatus {
    Pending,
    Processing,
    Finished,
    Failed,
}

pub struct TaskItem {
    pub task_type: String,
    pub folder_path: String,
    pub status: TaskStatus,               // 默认为 "pending"
    pub progress: i32,                // 默认为 0
    pub total: i32,                   // 可由调用方设定
    pub result_summary: Option<String>,
    pub error_message: Option<String>,
    pub created_at: NaiveDateTime,
    pub updated_at: NaiveDateTime,
}
#[derive(Debug, sqlx::FromRow, Serialize, Deserialize)]
pub struct TaskResultItem {
    pub task_id: String,
    pub result: String, // 这里是 JSON 字符串，解析时你可以转 Vec<Vec<String>>
}
#[derive(Debug, Serialize, FromRow)]

pub struct SelectTaskResultItem {
    pub id: i64,
    pub task_id: String,
    pub result: String,
    pub created_at: String, // 或 chrono::NaiveDateTime
}

#[derive(Debug, FromRow, Serialize)]
pub struct SelectTaskItem {
    pub id: i64,
    pub task_type: String,
    pub folder_path: String,
    pub status: String,
    pub progress: i32,
    pub total: i32,
    pub result_path: Option<String>,
    pub result_summary: Option<String>,
    pub error_message: Option<String>,
    pub created_at: String,
    pub updated_at: String,
}

#[derive(Serialize)]
pub struct ImageMeta {
    pub file_path: String,
    pub file_size: u64,
    pub file_update_time: u64, // 使用时间戳（秒）
    pub is_select: bool
}

#[derive(Serialize, Deserialize)]
pub struct HashItem {
    pub file_path: String,
    pub hash_bytes: Vec<u8>, // 直接存原始字节
}


pub enum UserFrom {
    Weibo,
    Douyin,
    RedNote,
    Bilibili,
}
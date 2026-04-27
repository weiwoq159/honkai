use serde::{Deserialize, Serialize};
use sqlx::SqlitePool;

pub mod types {
    use super::*; // 确保继承外部导入
    #[derive(Debug, Clone, Serialize)]
    pub struct OpenFileDialog {
        pub current_page: String,
    }
    #[derive(Debug, Clone, Serialize)]
    pub struct SImageList {
        pub current_page: String,
        pub image_list: Vec<String>,
    }
}

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
pub struct MyState {
    pub pool: SqlitePool,
}

pub struct BlogParams<'a> {
    pub blog_id: &'a str,
    pub user_id: &'a str,
    pub text: &'a str,
    pub text_raw: &'a str,
    pub create_time: &'a str,
    pub url: &'a str,
    pub blog_type: &'a str,
    pub preview_url: &'a str,
}

#[derive(Debug, Deserialize)]
pub struct AppConfig {
    pub get_weibo_list_url: String,
    pub get_weibo_user_url: String,
    pub user_agent: String,
    pub referer: String,
    pub weixin_referer: String,
}

#[derive(Serialize)]
pub struct WeiboUrl {
    pub url: Vec<String>,
    pub preview_url: Vec<String>,
}

#[derive(Serialize)]
struct OkData {
    url: Vec<String>,
    preview_url: Vec<String>,
}

#[derive(Serialize)]
struct ImageList {
    Ok: OkData,
}

#[derive(Serialize)]
struct Data {
    image_list: ImageList,
    user_name: String,
}

#[derive(Serialize)]
struct IResponse<T> {
    status: i32,
    message: String,
    data: T,
}

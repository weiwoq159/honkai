use crate::crawler::weibo_crawler::fetch_weibo_data;
use crate::crawler::weixin_crawler::fetch_weixin_data;
use crate::structs::index::SResponse;
use reqwest::Client;
use serde_json::Value;
use tauri::AppHandle;
use url::Url;

#[tauri::command]
pub async fn parse_input_url(
    app_handle: AppHandle,
    parse_url: String,
) -> Result<SResponse<Option<Value>>, SResponse<String>> {
    let client = Client::new();

    let parsed_url = match Url::parse(&parse_url) {
        Ok(url) => url,
        Err(err) => {
            return Err(SResponse {
                status: 500,
                message: format!("URL 解析失败: {}", err),
                data: String::new(),
            });
        }
    };

    match parsed_url.host_str() {
        Some(host) if host.contains("weibo.com") => {
            fetch_weibo_data(&app_handle, &client, &parsed_url).await
        }
        Some(host) if host.contains("weixin.qq") => {
            fetch_weixin_data(&app_handle, &client, &parsed_url).await
        }
        Some(_) => Err(SResponse {
            status: 500,
            message: "不支持的域名".to_string(),
            data: String::new(),
        }),
        None => Err(SResponse {
            status: 500,
            message: "URL 中没有有效的域名".to_string(),
            data: String::new(),
        }),
    }
}

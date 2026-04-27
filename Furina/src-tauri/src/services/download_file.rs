use crate::structs::index::SResponse;
use reqwest::{
    header::{HeaderMap, HeaderValue, REFERER, USER_AGENT},
    Client,
};
use serde_json::{json, Value};
use std::fs;
use std::path::PathBuf;
use std::time::{SystemTime, UNIX_EPOCH};
use tokio::io::AsyncWriteExt;

/// 获取微博文件名
fn get_weibo_filename(url: &str) -> Option<String> {
    url.split('/')
        .last()?
        .split('?')
        .next()
        .map(|s| s.to_string())
}

/// 获取微信文件名
fn get_wechat_filename(url: &str) -> Option<String> {
    url.split('/')
        .rev()
        .nth(1)
        .map(|s| format!("wechat_{}", s))
}

/// 兜底文件名：时间戳
fn get_fallback_filename() -> String {
    SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap_or_default()
        .as_millis()
        .to_string()
}

/// 根据 origin 和 url 选择合适的命名策略
fn get_filename_by_origin(origin: &str, url: &str) -> String {
    match origin {
        "weibo" => get_weibo_filename(url),
        "weixin" | "wechat" => get_wechat_filename(url),
        _ => None,
    }
    .unwrap_or_else(get_fallback_filename)
}

/// 构造目标保存文件夹路径
fn build_target_path(folder_path: &str, origin: &str, user_name: &Option<String>) -> PathBuf {
    let mut path = PathBuf::from(folder_path);
    let sub_folder = user_name
        .as_deref()
        .filter(|name| !name.trim().is_empty())
        .map(|name| format!("{}_{}", name, origin))
        .unwrap_or_else(|| origin.to_string());
    path.push(sub_folder);
    path
}

#[tauri::command]
pub async fn download_file(
    _app_handle: tauri::AppHandle,
    folder_path: String,
    download_file_url: Vec<String>,
    origin: String,
    user_name: Option<String>,
    file_name: Option<String>,
    file_type: String,
) -> Result<SResponse<Value>, String> {
    let client = Client::new();
    let mut headers = HeaderMap::new();

    headers.insert(
        USER_AGENT,
        HeaderValue::from_static("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.5845.97 Safari/537.36 Core/1.116.531.400 QQBrowser/19.3.6527.400"),
    );

    if origin == "weibo" {
        headers.insert(REFERER, HeaderValue::from_static("https://weibo.com/"));
    } else if origin == "wechat" {
        headers.insert(REFERER, HeaderValue::from_static("https://mp.weixin.qq.com/"));
    }

    let target_path = build_target_path(&folder_path, &origin, &user_name);
    if !target_path.exists() {
        fs::create_dir_all(&target_path).map_err(|e| format!("创建文件夹失败: {}", e))?;
        println!("📂 文件夹已创建: {:?}", target_path);
    } else {
        println!("📂 文件夹已存在: {:?}", target_path);
    }

    let mut saved_files = Vec::new();
    let actual_file_type = if file_type == "livp" { "livp" } else { &file_type };

    for image_url in &download_file_url {
        println!("下载中: {}", image_url);

        let image_name = file_name
            .as_ref()
            .map_or_else(|| get_filename_by_origin(&origin, image_url), Clone::clone);

        let file_path = target_path.join(format!("{}.{}", image_name, actual_file_type));

        if tokio::fs::metadata(&file_path).await.is_ok() {
            println!("📦 已存在: {}", file_path.to_string_lossy());
            saved_files.push(file_path.to_string_lossy().to_string());
            continue;
        }

        let resp = client
            .get(image_url)
            .headers(headers.clone())
            .send()
            .await
            .map_err(|e| format!("下载失败: {}", e))?;

        if !resp.status().is_success() {
            println!("⚠️ 状态码异常: {}", resp.status());
            continue;
        }

        let bytes = resp
            .bytes()
            .await
            .map_err(|e| format!("读取数据失败: {}", e))?;

        let mut file = tokio::fs::File::create(&file_path)
            .await
            .map_err(|e| format!("创建文件失败: {}", e))?;

        file.write_all(&bytes)
            .await
            .map_err(|e| format!("写入失败: {}", e))?;

        println!("✅ 已保存: {}", file_path.to_string_lossy());
        saved_files.push(file_path.to_string_lossy().to_string());
    }

    Ok(SResponse::success(json!({ "savedFiles": saved_files })))
}
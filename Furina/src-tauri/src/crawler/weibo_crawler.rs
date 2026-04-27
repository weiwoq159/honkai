use crate::structs::index::{SResponse, UserFrom};
// use regex::Regex;
use reqwest::header::{HeaderMap, HeaderValue, USER_AGENT, COOKIE};
use serde_json::{json, Value};
use tauri::AppHandle;
use url::Url;
use crate::services::database::{insert_user_table};
fn extract_weibo_uid(parsed_url: &Url) -> Option<String> {
    let mut segments = parsed_url.path_segments()?;
    let first = segments.next()?;
    if first == "u" {
        segments.next().map(|s| s.to_string())
    } else {
        Some(first.to_string()) // fallback: weibo.com/12345678 这种格式
    }
}

async fn fetch_weibo_username(client: &reqwest::Client, weibo_cookie: &str, uid: &str) -> Result<String, String> {
    print!("123");
    let mut headers = HeaderMap::new();
    let url = "https://weibo.com/ajax/profile/info";
    headers.insert(
        USER_AGENT,
        HeaderValue::from_static("Mozilla/5.0"),
    );
    headers.insert(COOKIE, HeaderValue::from_str(weibo_cookie).unwrap()); // ✅ 设置 Cookie
    let resp = client
        .get(url)
        .headers(headers)
        .query(&[("uid", uid)])  // ✅ 设置查询参数
        .send()
        .await
        .map_err(|e| format!("请求失败: {}", e))?;
    let data = resp.json::<serde_json::Value>().await.map_err(|e| format!("用户信息格式化失败:{}", e))?;
    let user_name = data["data"]["user"]["screen_name"]
        .as_str()
        .ok_or("未获取到用户昵称")?
        .to_string();
    return Ok(user_name);
}


pub async fn fetch_weibo_data(
    app_handle: &AppHandle,
    _client: &reqwest::Client,
    parsed_url: &Url,
    weibo_cookie: &str
) -> Result<SResponse<Value>, String> {
    let weibo_uid = match extract_weibo_uid(parsed_url) {
        Some(uid) => uid,
        _ => return Err(format!("用户id提取失败"))
    };
    println!("{}", weibo_uid);
    let weibo_user_name = match fetch_weibo_username(_client, weibo_cookie, &weibo_uid).await {
        Ok(user_name) => user_name,
        _ => return Err("用户名提取失败".to_string()),
    };
    let _ = insert_user_table(app_handle, &weibo_user_name, &weibo_uid, UserFrom::Weibo).await;
    println!("{}", weibo_user_name);

    println!("{}", weibo_uid);
    Ok(SResponse::success(json!({
        "from": "weibo",
    })))
}

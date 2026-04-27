use crate::structs::index::{AppConfig, BlogParams, SResponse};
use crate::structs::weibo_user_info::WeiboProfileResp;
use crate::utils::database::{
    insert_blog_item, insert_user, select_url_from_weibo, select_user_by_weibo_id,
};
use crate::utils::utils::{build_headers, load_config};
use rand::Rng;
use reqwest::header::{HeaderMap, HeaderValue, REFERER, USER_AGENT};
use serde_json::Value;
use std::borrow::Cow;
use tokio::time::{sleep, Duration};
use url::Url;

pub fn extract_weibo_id(parsed_url: &Url) -> Option<String> {
    match parsed_url
        .path()
        .split('/')
        .collect::<Vec<&str>>()
        .as_slice()
    {
        ["", "u", id, ..] if id.parse::<u64>().is_ok() => Some(id.to_string()),
        ["", "status", id, ..] if id.parse::<u64>().is_ok() => Some(id.to_string()),
        ["", "profile", id, ..] if id.parse::<u64>().is_ok() => Some(id.to_string()),
        ["", "n", id, ..] if id.parse::<u64>().is_ok() => Some(id.to_string()),
        [uid, "status", id, ..] if uid.parse::<u64>().is_ok() && id.parse::<u64>().is_ok() => {
            Some(id.to_string())
        }
        _ => None,
    }
}

#[tauri::command]
pub async fn fetch_weibo_data(
    app_handle: &tauri::AppHandle,
    _client: &reqwest::Client,
    parsed_url: &Url,
) -> Result<SResponse<Option<Value>>, SResponse<String>> {
    let config = load_config();

    let uid = match extract_weibo_id(parsed_url) {
        Some(uid) => uid, // 提取成功，返回 uid
        None => {
            return Err(SResponse {
                // 提取失败，提前返回错误
                status: 400,
                message: "无法从 URL 提取微博 ID".to_string(),
                data: String::new(),
            });
        }
    };
    let (user_name, weibo_id) = match select_user_by_weibo_id(app_handle, &uid).await {
        Ok((username, weibo_id)) => {
            println!("数据库已存在用户：{}", username);
            (username, weibo_id)
        }
        Err(e) => {
            println!("数据库无用户或查询失败，调接口");

            let resp = _client
                .get(&config.get_weibo_user_url)
                .headers(build_headers(&config))
                .query(&[("uid", &uid)])
                .send()
                .await
                .unwrap();

            let text = resp.text().await.unwrap();
            println!("{}", text);

            let json: WeiboProfileResp = serde_json::from_str(&text).unwrap();
            let user_name = json.data.user.screen_name;

            let _ = insert_user(app_handle, &user_name, "weibo_id", &uid).await;
            (user_name, uid.clone())
        }
    };

    let mut current_page = 1;
    let mut since_id = String::new();
    let mut all_blogs = Vec::new();

    loop {
        let mut req = _client
            .get(&config.get_weibo_list_url)
            .headers(build_headers(&config))
            .query(&[
                ("uid", &uid),
                ("feature", &"0".to_string()),
                ("page", &current_page.to_string()),
            ]);

        if !since_id.is_empty() {
            req = req.query(&[("since_id", &since_id)]);
        }

        let resp = req.send().await.unwrap();
        let blog_json: Value = resp.json().await.unwrap();

        let list: Cow<'_, [Value]> = blog_json
            .get("data")
            .and_then(|d| d.get("list"))
            .and_then(|l| l.as_array())
            .map(|arr| Cow::Borrowed(arr.as_slice()))
            .unwrap_or_else(|| Cow::Owned(vec![]));

        println!("第 {} 页，获取 {} 条数据", current_page, list.len());

        if list.is_empty() {
            println!("列表为空，结束循环");
            break;
        }
        let mut has_new = false;

        for item in list.iter() {
            let analysis_extra = item
                .get("analysis_extra")
                .and_then(|v| v.as_str())
                .unwrap_or("");

            let text_raw = item.get("text_raw").and_then(|v| v.as_str()).unwrap_or("");

            if analysis_extra.contains("mblog_rt_mid") {
                if text_raw.contains(&user_name) {
                    // println!("转发中含本人用户名，入库");
                    if insert_blog(app_handle, item).await {
                        has_new = true;
                    }
                } else {
                    // println!("跳过普通转发");
                }
            } else if analysis_extra.contains("profile_insert_type:like_status") {
                // println!("跳过点赞");
            } else {
                // println!("本人发布，入库");
                if insert_blog(app_handle, item).await {
                    has_new = true;
                };
            }
        }
        if !has_new {
            println!("本页无新增，终止循环");
            break;
        }
        // let _ = inter_list(app_handle, &list, &user_name).await;
        all_blogs.extend_from_slice(&list);

        // 更新 since_id，如果需要
        since_id = blog_json
            .get("data")
            .and_then(|d| d.get("since_id"))
            .and_then(|s| s.as_str())
            .unwrap_or("")
            .to_string();

        current_page += 1;
        let delay = rand::rng().random_range(1.0..=3.0);
        println!("暂停 {} 秒", delay);
        sleep(Duration::from_secs_f64(delay)).await;
    }
    let sql_list = select_url_from_weibo(app_handle, &uid).await;

    Ok(SResponse {
        message: "微博数据获取成功".to_string(),
        status: 200,
        data: Some(serde_json::json!({
            "user_name": user_name,
            "image_list": sql_list,
        })),
    })
}

async fn insert_blog(app_handle: &tauri::AppHandle, item: &Value) -> bool {
    // 判断是否有图
    let has_pic = item
        .get("pic_ids")
        .and_then(|v| v.as_array())
        .map(|arr| !arr.is_empty())
        .unwrap_or(false);

    if !has_pic {
        return false;
    }

    let blog_id = match item.get("idstr").and_then(|v| v.as_str()) {
        Some(id) => id,
        None => return false,
    };

    let user_id = match item
        .get("user")
        .and_then(|u| u.get("idstr"))
        .and_then(|v| v.as_str())
    {
        Some(id) => id,
        None => return false,
    };

    let text_raw = item.get("text_raw").and_then(|v| v.as_str()).unwrap_or("");
    let created_at = item
        .get("created_at")
        .and_then(|v| v.as_str())
        .unwrap_or("");
    let types = "Image";

    // 提取图片 URL
    let image_urls = item
        .get("pic_infos")
        .and_then(|p| p.as_object())
        .map(|infos| {
            infos
                .iter()
                .filter_map(|(_, pic_info)| {
                    pic_info
                        .get("original")
                        .and_then(|m| m.get("url"))
                        .and_then(|u| u.as_str())
                        .map(|s| s.to_string())
                })
                .collect::<Vec<String>>()
        })
        .unwrap_or_default();

    let preview_urls = item
        .get("pic_infos")
        .and_then(|p| p.as_object())
        .map(|infos| {
            infos
                .iter()
                .filter_map(|(_, pic_info)| {
                    pic_info
                        .get("largest")
                        .and_then(|m| m.get("url"))
                        .and_then(|u| u.as_str())
                        .map(|s| s.to_string())
                })
                .collect::<Vec<String>>()
        })
        .unwrap_or_default();

    if image_urls.is_empty() {
        return false;
    }

    match insert_blog_item(
        app_handle,
        BlogParams {
            blog_id,
            user_id,
            text: text_raw,
            text_raw,
            create_time: created_at,
            url: &image_urls.join(","),
            preview_url: &preview_urls.join(","),
            blog_type: types,
        },
    )
    .await
    {
        Ok(inserted) => inserted,
        Err(_) => false,
    }
}

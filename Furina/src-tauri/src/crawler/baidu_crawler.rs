use crate::services::database::{
    insert_media_item, select_md5_set_by_from, select_media_item_by_from,update_media_item
};
use crate::structs::index::MediaItem;
use crate::structs::index::SResponse;
use chrono::Utc;
use futures::stream::{FuturesUnordered, StreamExt};
use reqwest::{
    header::{HeaderMap, HeaderValue, USER_AGENT},
    Client,
};
use serde_json::{json, Value};
use std::collections::HashSet;
use std::path::Path;
use std::sync::Arc;
use tokio::sync::Semaphore;

const MAX_CONCURRENCY: usize = 10;

#[tauri::command]
pub async fn fetch_baidu_image_list(
    app_handle: tauri::AppHandle,
    bdstoken: String,
    baidu_cookie: String,
) -> Result<SResponse<Value>, String> {
    let client = Client::new();
    let mut headers = HeaderMap::new();
    headers.insert(
        USER_AGENT,
        HeaderValue::from_static("Mozilla/5.0 (iPhone; CPU iPhone OS 19_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.61(0x18003d28) NetType/WIFI Language/zh_CN"),
    );
    headers.insert("Cookie", HeaderValue::from_str(&baidu_cookie).unwrap());
    println!("📦 初始化 header 和 client 完成");

    let mut current_cursor = String::new();
    let existing_md5s: HashSet<String> = select_md5_set_by_from(&app_handle, "baidu").await?;
    println!("🔍 数据库中已有 md5 数量: {}", existing_md5s.len());

    let semaphore = Arc::new(Semaphore::new(MAX_CONCURRENCY));
    let mut current_page = 1;
    // let mut is_flag = false;
    loop {
        println!(
            "➡️ 请求第 {} 页，cursor = '{}'",
            current_page, current_cursor
        );
        // if is_flag {
        //     break
        // }
        let url = format!(
            "https://photo.baidu.com/youai/file/v1/list?clienttype=70&bdstoken={}&need_thumbnail=1&need_filter_hidden=0{}",
            bdstoken,
            if current_cursor.is_empty() {
                "".to_string()
            } else {
                format!("&cursor={}", current_cursor)
            }
        );
        let resp = client
            .get(&url)
            .headers(headers.clone())
            .send()
            .await
            .map_err(|e| format!("下载失败: {}", e))?;
        let json_val: Value = resp
            .json()
            .await
            .map_err(|e| format!("解析 JSON 失败: {}", e))?;
        let list: Vec<Value> = match json_val.get("list").and_then(|v| v.as_array()) {
            Some(l) => l.iter().cloned().collect(),
            None => break,
        };
        
        if list.is_empty() {
            println!("🛑 当前页返回 list 为空，跳出分页循环");
            break;
        }
        let mut tasks = FuturesUnordered::new();

        for item in list.into_iter() {
            let item = item.clone(); // 复制整个 JSON 对象

            let thumbs = match item.get("thumburl").and_then(|v| v.as_array()) {
                Some(t) => t.to_vec(), // 复制 thumbs 数组，确保不再借用 item
                None => continue,
            };

            let fsid = match item.get("fsid").and_then(|v| v.as_u64()) {
                Some(f) => f,
                None => continue,
            };

            let md5_code = fsid.to_string();
            if existing_md5s.contains(&md5_code) {
                continue;
                // is_flag = true;
                // break;
            }

            let preview_url = thumbs
                .get(0)
                .and_then(|v| v.as_str())
                .unwrap_or("")
                .to_string();
            let url = thumbs
                .get(1)
                .and_then(|v| v.as_str())
                .unwrap_or("")
                .to_string();
            let path_str = item
                .get("path")
                .and_then(|v| v.as_str())
                .unwrap_or("")
                .to_string();
            let extension = Path::new(&path_str)
                .extension()
                .and_then(|ext| ext.to_str())
                .unwrap_or("")
                .to_lowercase();
            let file_name = Path::new(&path_str)
                .file_stem()
                .and_then(|s| s.to_str())
                .unwrap_or("")
                .to_string();
            let date_time_str = item
                .get("extra_info")
                .and_then(|e| e.get("date_time"))
                .and_then(|v| v.as_str())
                .map(|s| s.to_string())
                .unwrap_or_else(|| Utc::now().naive_utc().to_string());

            let permit = semaphore.clone().acquire_owned().await.unwrap();
            let headers = headers.clone();
            let client = client.clone();
            let bdstoken = bdstoken.clone();
            let app_handle = app_handle.clone();

            tasks.push(tokio::spawn(async move {
                let _permit = permit;
                println!("🚀 开始处理文件 fsid: {}", md5_code);

                let download_res = client
                    .get(format!("https://photo.baidu.com/youai/file/v2/download?clienttype=70&bdstoken={}&fsid={}", bdstoken, md5_code))
                    .headers(headers)
                    .send()
                    .await
                    .map_err(|e| format!("下载失败: {}", e))?;

                let download_json: Value = download_res.json().await.map_err(|e| format!("解析 JSON 失败: {}", e))?;
                let dlink = download_json.get("dlink").and_then(|v| v.as_str()).unwrap_or("").to_string();

                let item = MediaItem {
                    preview_url,
                    url,
                    media_type: Some("image".to_string()),
                    format: Some(extension),
                    blog_id: None,
                    user_id: None,
                    created_at: Some(date_time_str),
                    origin_from: Some("baidu".to_string()),
                    is_deleted: Some(0),
                    file_name: Some(file_name.clone()),
                    md5_code: Some(md5_code),
                    download_url: Some(dlink),
                };

                let _ = insert_media_item(&app_handle, item).await;
                println!("✅ 成功插入文件: {}", file_name);
                Ok::<_, String>(())
            }));
        }

        while let Some(res) = tasks.next().await {
            if let Err(e) = res {
                println!("⚠️ 子任务执行失败: {:?}", e);
            }
        }
        if let Some(cursor_val) = json_val.get("cursor").and_then(|v| v.as_str()) {
            if cursor_val.is_empty() {
                println!("🔚 cursor 为空，结束分页");
                break;
            }
            current_cursor = cursor_val.to_string();
        } else {
            println!("🔚 无 cursor 字段，结束分页");
            break;
        }
        current_page += 1
    }
    println!("📊 分页抓取结束，准备查询数据库结果");


    let image_arr = select_media_item_by_from(&app_handle, "baidu", false).await?;
    

    if let Some(arr) = image_arr.as_array() {
        println!("📦 返回前端图片数量: {}", arr.len());
    } else {
        println!("⚠️ image_arr 不是数组，实际类型: {:?}", image_arr);
    }
    Ok(SResponse::success(json!({
        "imageList": image_arr,
        "from": "baidu",
        "userName": "baidu"
    })))
}



#[tauri::command]
pub async fn resolve_media_list(app_handle: tauri::AppHandle, bdstoken: String) -> Result<SResponse<Value>, String> {
    // 1. 查询图片数据，返回所有没有 download_url 的图片
    let image_arr = select_media_item_by_from(&app_handle, "baidu", true).await?;

    if let Some(arr) = image_arr.as_array() {
        println!("📦 返回前端图片数量: {}", arr.len());
    } else {
        println!("⚠️ image_arr 不是数组，实际类型: {:?}", image_arr);
    }
    // 2. 遍历每个图片项，查找没有 download_url 的图片
    let mut tasks = FuturesUnordered::new();
    for item in image_arr.as_array().unwrap_or(&vec![]) {
        if item.get("download_url").and_then(|v| v.as_str()).unwrap_or("").is_empty() {
            if let Some(fsid) = item.get("md5_code").and_then(|v| v.as_str()) {
                // 3. 获取 fsid，重新请求下载链接
                let fsid = fsid.to_string();
                let app_handle = app_handle.clone();
                let bdstoken_clone = bdstoken.clone();
                println!("{}", fsid);
                tasks.push(tokio::spawn(async move {
                    // 重新调用接口获取 download_url
                    let client = reqwest::Client::new();
                    let download_res = client
                        .get(format!(
                            "https://photo.baidu.com/youai/file/v2/download?clienttype=70&bdstoken={}&fsid={}",
                            bdstoken_clone, fsid
                        ))
                        .send()
                        .await
                        .map_err(|e| format!("下载失败: {}", e));
                    println!("{:?}", download_res);
                    if let Ok(resp) = download_res {
                        let download_json: serde_json::Value = resp
                            .json()
                            .await
                            .map_err(|e| format!("解析 JSON 失败: {}", e))?;
                        println!("{:?}", download_json);
                        let dlink = download_json
                            .get("dlink")
                            .and_then(|v| v.as_str())
                            .unwrap_or("")
                            .to_string();
                        if !dlink.is_empty() {
                            // 更新数据库中的数据
                            let _ = update_media_item(&app_handle, &fsid, &dlink).await;
                            println!("✅ 成功更新图片项的 download_url");
                        } else {
                            println!("⚠️ 无法获取有效的 download_url");
                        }
                    } else {
                        println!("❌ 请求 download_url 时失败");
                    }

                    Ok::<_, String>(())
                }));
            }
        }
    }

    // 等待所有并发任务完成
    while let Some(_) = tasks.next().await {}

    // 5. 返回更新后的数据
    let updated_image_arr = select_media_item_by_from(&app_handle, "baidu", true).await?;

    Ok(SResponse::success(json!({
        "imageList": updated_image_arr,
        "from": "baidu",
        "userName": "baidu"
    })))
}

use crate::services::database::{insert_media_item, select_media_item_by_from};
use crate::structs::index::{MediaItem, SResponse};
use chrono::Utc;
use futures::stream::{FuturesUnordered, StreamExt};
use reqwest::{
    header::{HeaderMap, HeaderValue, USER_AGENT},
    Client,
};
use serde_json::{json, Value};
use std::path::Path;
use std::sync::Arc;
use tokio::sync::Semaphore;

const MAX_CONCURRENCY: usize = 10;

#[tauri::command]
pub async fn fetch_yan_image_list(
    app_handle: tauri::AppHandle,
) -> Result<SResponse<Value>, String> {
    let client = Client::new();
    let mut headers = HeaderMap::new();
    headers.insert(
        USER_AGENT,
        HeaderValue::from_static("Mozilla/5.0 (iPhone; CPU iPhone OS 19_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.61(0x18003d28) NetType/WIFI Language/zh_CN"),
    );

    let semaphore = Arc::new(Semaphore::new(MAX_CONCURRENCY));
    let mut current = 1;

    loop {
        println!("➡️ 请求第 {} 页", current);
        let resp = client
            .get(format!(
                "https://llf666.com.cn/api/article/sj/mian?pageNum={}&pageSize=60&articleStatus=%E5%8F%91%E5%B8%83",
                current
            ))
            .headers(headers.clone())
            .send()
            .await
            .map_err(|e| format!("下载失败: {}", e))?;

        let json: Value = resp
            .json()
            .await
            .map_err(|e| format!("解析 JSON 失败: {}", e))?;

        let items = match json
            .get("data")
            .and_then(|d| d.get("items"))
            .and_then(|v| v.as_array())
        {
            Some(arr) if !arr.is_empty() => arr,
            _ => {
                println!("🔚 页 {} 无有效数据，结束", current);
                break;
            }
        };

        let mut tasks = FuturesUnordered::new();
        let mut page_inserted = 0;

        for item in items {
            let Some(article_src) = item.get("articleSrc").and_then(|v| v.as_str()) else {
                println!("⚠️ 缺少 articleSrc，跳过");
                continue;
            };

            let updated_at_str = item
                .get("articleUpdatedAt")
                .and_then(|v| v.as_str())
                .map(|s| s.to_string())
                .unwrap_or_else(|| Utc::now().naive_utc().to_string());

            let file_name = Path::new(article_src)
                .file_stem()
                .and_then(|s| s.to_str())
                .unwrap_or("")
                .to_string();

            let preview_url = article_src.to_string();
            let download_url = article_src.to_string();
            let md5_code = article_src.to_string();

            let permit = semaphore.clone().acquire_owned().await.unwrap();
            let app_handle = app_handle.clone();

            let item = MediaItem {
                preview_url,
                url: article_src.to_string(),
                media_type: Some("image".to_string()),
                format: Some("png".to_string()),
                blog_id: None,
                user_id: None,
                created_at: Some(updated_at_str),
                origin_from: Some("yan".to_string()),
                is_deleted: Some(0),
                file_name: Some(file_name),
                md5_code: Some(md5_code),
                download_url: Some(download_url),
            };

            tasks.push(tokio::spawn(async move {
                let _permit = permit;
                match insert_media_item(&app_handle, item).await {
                    Ok(rows) if rows > 0 => {
                        println!("✅ 插入成功");
                        Ok::<_, String>(1)
                    }
                    Ok(_) => {
                        println!("⚠️ 跳过重复");
                        Ok(0)
                    }
                    Err(e) => {
                        eprintln!("❌ 插入失败: {}", e);
                        Err(e)
                    }
                }
            }));
        }

        // 等待所有任务完成
        while let Some(res) = tasks.next().await {
            match res {
                Ok(Ok(1)) => page_inserted += 1,
                _ => {} // 忽略失败
            }
        }

        println!("📦 当前第 {} 页插入 {} 条", current, page_inserted);

        if page_inserted == 0 {
            println!("📴 本页数据全部在库中，提前终止");
            break;
        }

        current += 1;
    }

    let image_arr = select_media_item_by_from(&app_handle, "yan", false).await?;
    Ok(SResponse::success(json!({
        "imageList": image_arr,
        "from": "yan",
        "userName": "yan"
    })))
}

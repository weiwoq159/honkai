use crate::structs::index::SResponse;
use regex::Regex;
use reqwest::header::{HeaderMap, HeaderValue, USER_AGENT};
use serde_json::{json, Value};
use tauri::AppHandle;
use url::Url;

/// 提取 `var picturePageInfoList = "..."` 中的 JSON 字符串
fn extract_json(input: &str) -> Option<String> {
    let re = Regex::new(r#"picturePageInfoList\s*=\s*"(.*?)";"#).ok()?;
    re.captures(input)
        .and_then(|cap| cap.get(1))
        .map(|m| m.as_str().to_string())
}

/// 清洗 JSON 字符串，转为标准格式
fn clean_json_string(raw: &str) -> String {
    let replaced = raw
        .replace('\'', "\"")
        .replace(r"\x26amp;amp;", "&")
        .replace(r"\\", "");

    let re_trailing_comma = Regex::new(r",\s*\]").unwrap();
    re_trailing_comma.replace_all(&replaced, "]").to_string()
}

/// 构建最终图片列表：过滤、转换格式
fn build_final_result(json: &Value) -> Result<Value, String> {
    let arr = json
        .as_array()
        .ok_or_else(|| "返回的数据不是数组".to_string())?;

    let mut urls = Vec::new();

    for item in arr {
        // 提取 url
        let url = match item.get("cdn_url").and_then(|v| v.as_str()) {
            Some(u) => u,
            None => {
                println!("⚠️ 缺少 cdn_url: {:?}", item);
                continue;
            }
        };

        // 提取 width
        let width = match item
            .get("width")
            .and_then(|v| v.as_str())
            .and_then(|s| s.parse::<u64>().ok())
        {
            Some(w) => w,
            None => {
                println!("⚠️ width 无效: {:?}", item.get("width"));
                continue;
            }
        };

        // 提取 height
        let height = match item
            .get("height")
            .and_then(|v| v.as_str())
            .and_then(|s| s.parse::<u64>().ok())
        {
            Some(h) => h,
            None => {
                println!("⚠️ height 无效: {:?}", item.get("height"));
                continue;
            }
        };

        // 过滤规则
        if width < 800 || width == height {
            println!("🔍 跳过不符合尺寸要求: {}x{}", width, height);
            continue;
        }

        urls.push(json!({
            "url": url,
            "preview_url": url
        }));
    }

    Ok(json!(urls))
}

/// 主函数：拉取微信图集页面，解析图片列表
pub async fn fetch_weixin_data(
    _app_handle: &AppHandle,
    client: &reqwest::Client,
    parsed_url: &Url,
) -> Result<SResponse<Value>, String> {
    let url = parsed_url.as_str();

    let mut headers = HeaderMap::new();
    headers.insert(
        USER_AGENT,
        HeaderValue::from_static("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.5845.97 Safari/537.36 Core/1.116.531.400 QQBrowser/19.3.6527.400"),
    );

    // 请求页面内容
    let resp = client
        .get(url)
        .headers(headers)
        .send()
        .await
        .map_err(|e| format!("请求失败: {}", e))?;

    let text = resp
        .text()
        .await
        .map_err(|e| format!("读取响应失败: {}", e))?;

    // 提取 JSON 内容
    let raw_json_str = extract_json(&text).ok_or("未找到图集 JSON 数据")?;
    let clean_str = clean_json_string(&raw_json_str);

    // 解析 JSON
    let parsed: Value =
        serde_json::from_str(&clean_str).map_err(|_| "图片数据解析失败".to_string())?;

    let final_result = build_final_result(&parsed)?;

    Ok(SResponse::success(json!({
        "imageList": final_result,
        "from": "weixin",
        "userName": ""
    })))
}

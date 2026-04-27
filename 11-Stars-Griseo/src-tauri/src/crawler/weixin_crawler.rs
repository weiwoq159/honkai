use crate::structs::index::SResponse;
use crate::utils::utils::load_config;
use regex::Regex;
use reqwest::header::{HeaderMap, HeaderValue, REFERER, USER_AGENT};
use serde_json::{json, Value};
use url::Url;

fn extract_json(input: &str) -> Option<String> {
    // 匹配从 `var picturePageInfoList = "` 开始，到 `"` 结束的内容
    let re = Regex::new(r#"picturePageInfoList\s*=\s*"(.*?)";"#).unwrap();

    re.captures(input)
        .and_then(|cap| cap.get(1))
        .map(|m| m.as_str().to_string())
}
fn clean_json_string(raw: &str) -> String {
    let mut replaced = raw.replace('\'', "\"");
    replaced = replaced.replace(r"\x26amp;amp;", "&");

    // 用正则去除数组尾部多余的逗号
    let re_trailing_comma = Regex::new(r",\s*\]").unwrap();
    replaced = re_trailing_comma.replace_all(&replaced, "]").to_string();

    replaced
}
fn build_final_result(json: &Value) -> Result<Value, SResponse<String>> {
    let arr = json.as_array().ok_or_else(|| SResponse {
        status: 500,
        message: "返回的数据不是数组".to_string(),
        data: "类型错误".to_string(),
    })?;

    let mut urls = Vec::new();
    let mut preview_urls = Vec::new();

    for item in arr {
        let url = match item.get("cdn_url").and_then(|v| v.as_str()) {
            Some(v) => v,
            None => continue, // 缺少 cdn_url，跳过
        };

        // 提取 width 和 height，尝试解析为整数
        let width = match item
            .get("width")
            .and_then(|v| v.as_str())
            .and_then(|s| s.parse::<u32>().ok())
        {
            Some(w) => w,
            None => continue, // 缺少或不合法，跳过
        };

        let height = match item
            .get("height")
            .and_then(|v| v.as_str())
            .and_then(|s| s.parse::<u32>().ok())
        {
            Some(h) => h,
            None => continue, // 缺少或不合法，跳过
        };

        // 进一步判断尺寸是否合规，假设要求宽高都 > 200
        if width < 970 || height < 200 {
            continue;
        }

        // 符合规范，加入结果
        urls.push(url.to_string());
        preview_urls.push(format!("{}?preview=1", url));
    }

    Ok(json!({
        "url": urls,
        "preview_url": preview_urls
    }))
}

pub async fn fetch_weixin_data(
    app_handle: &tauri::AppHandle,
    _client: &reqwest::Client,
    parsed_url: &Url,
) -> Result<SResponse<Option<Value>>, SResponse<String>> {
    let url = parsed_url.as_str();
    let config = load_config();
    let mut headers = HeaderMap::new();
    headers.insert(
        USER_AGENT,
        HeaderValue::from_str(&config.user_agent).unwrap(),
    );
    let resp = _client.get(url).headers(headers).send().await.unwrap();
    let text: String = resp.text().await.unwrap();
    let json_content = extract_json(&text).unwrap();
    let clean_text = clean_json_string(&json_content);

    println!("清洗后：{}", clean_text);

    let result: serde_json::Result<Value> = serde_json::from_str(&clean_text);
    let json = result.map_err(|e| SResponse {
        status: 500,
        message: "图片数据解析失败".to_string(),
        data: e.to_string(),
    })?;
    let final_result = build_final_result(&json)?;

    // 必须返回 Result 类型
    Ok(SResponse {
        status: 200,
        message: "微信数据获取成功".to_string(),
        data: Some(json!({
            "user_name": "123",
            "image_list": {"Ok": final_result}
        })),
    })
}

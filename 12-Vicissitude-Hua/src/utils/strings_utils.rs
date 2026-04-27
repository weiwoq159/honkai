use std::collections::HashMap;
use url::{Url, Host};
use serde_json::Value;
use reqwest;
use crate::public::tiktok::DouyinUrls;
use regex::Regex;
use std::fs::File;
use std::path::Path;
use std::io::Write;
use crate::public::constans::ImageItem;
use std::time::{SystemTime, UNIX_EPOCH};
use std::fs;
use std::io::copy;

fn timestamp_ms() -> u64 {
    SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .expect("Time went backwards")
        .as_millis() as u64  // 转换为毫秒
}

// 平台分类（不变）
fn classify_url(url_str: &str) -> Result<String, String> {
    println!("原始URL: {}", url_str);
    let parsed_url = Url::parse(url_str)
        .map_err(|e| format!("无效的 URL: {}", e))?;
    
    let host = parsed_url.host()
        .ok_or("URL 不包含主机名")?;
    println!("解析到主机: {}", host);
    
    match host {
        Host::Domain(domain) => {
            if domain.contains("douyin.com") {
                Ok("douyin".into())
            } else if domain.contains("weibo.com") {
                Ok("weibo".into())
            } else if domain.contains("xiaohongshu.com") {
                Ok("xiaohongshu".into())
            } else if domain.contains("weixin.qq.com") {
                Ok("weixin".into())
            } else {
                Err(format!("不支持的平台域名: {}", domain))
            }
        }
        _ => Err("不支持IP地址格式的URL".into()),
    }
}

// 异步处理函数（错误类型统一为String）
pub async fn process_url(url: String) -> Result<String, String> {
    let platform = classify_url(&url)?;
    match platform.as_str() {
        "douyin" => process_douyin(&url).await,
        "weibo" => process_weibo(&url).await,
        "xiaohongshu" => process_xiaohongshu(&url).await,
        "weixin" => process_wechat(&url).await,
        _ => Err("不支持的平台".into()),
    }
}

// 抖音处理函数
async fn process_douyin(url: &str) -> Result<String, String> {
    let parsed_url = Url::parse(url).map_err(|e| format!("URL 解析失败: {}", e))?;
    let segments: Vec<_> = parsed_url.path_segments().ok_or("URL 无有效路径")?.collect();
    
    if segments.len() < 2 || segments[0] != "user" {
        return Err("URL 结构不符合预期: 应类似 /user/{ID}".into());
    }
    
    // 测试用API（实际使用时替换为真实抖音API）
    let douyin_post = DouyinUrls::default().user_post;
    
    // 添加错误转换
    let client = reqwest::Client::new();
    let resp = client
        .get("")
        .header("Accept", "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7")
        .header("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36")
        .send()
        .await
        .map_err(|e| format!("请求失败: {}", e))?
        .text()
        .await
        .map_err(|e| format!("JSON解析失败: {}", e))?;
    println!("{}", resp.contains("window.picture_page_info_list"));
    Ok(format!("成功获取抖音用户 {} 的数据", segments[1]))
}

// 微博处理函数
async fn process_weibo(_url: &str) -> Result<String, String> {
    // 模拟API请求
    let resp = reqwest::get("https://httpbin.org/ip")
        .await
        .map_err(|e| format!("请求失败: {}", e))?
        .text()
        .await
        .map_err(|e| format!("响应读取失败: {}", e))?;
    
    Ok(format!("微博处理完成，API响应: {}", resp))
}

// 小红书处理函数
async fn process_xiaohongshu(_url: &str) -> Result<String, String> {
    Ok("小红书功能正在开发中...".into())
}


async fn process_wechat(_url: &str) -> Result<String, String> {
    let re = Regex::new(r"(?s)window\.picture_page_info_list\s*=\s*(\[.*?\])")
    .map_err(|e| e.to_string())?; // 显式转换为 String

    let client = reqwest::Client::new();
    let resp = client
        .get(_url)
        .header("Accept", "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7")
        .header("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36")
        .send()
        .await
        .map_err(|e| format!("请求失败: {}", e))?
        .text()
        .await
        .map_err(|e| format!("JSON解析失败: {}", e))?;

    let json_str = match re.captures(&resp) {
        Some(caps) => caps.get(1).unwrap().as_str(),
        None => return Err("HTML中未找到picture_page_info_list".into()),
    };
    let format_str = clean_js_to_json(json_str);
    print!("{}",format_str);
    let parsed: Value = serde_json::from_str(&format_str)
    .map_err(|e| e.to_string())?; // 先解析为Value
    let client = reqwest::Client::new();

    if let Value::Array(images) = parsed {
        for img in images {
            if let Value::Object(img_data) = img {
                let width = img_data.get("width").and_then(|v| v.as_i64()).unwrap_or(0);
                let height = img_data.get("height").and_then(|v| v.as_i64()).unwrap_or(0);
                let cdn_url = img_data.get("cdn_url").and_then(|v| v.as_str()).unwrap_or("");
                if width > 960 {
                    downloa_image(&client, extract_image_id(cdn_url).unwrap(), cdn_url).await.unwrap()
                }
            }
        }
    }
    Ok("weixin...".into())
}

async fn downloa_image(client:  &reqwest::Client, file_name: &str, image_url: &str) -> Result<(), String>{
    print!("{}", file_name);
    let download_dir = r"D:\work\mq\Honkai\12-Vicissitude-Hua\picture";
    match fs::create_dir_all(download_dir) {
        Ok(_) => println!("目录创建成功"),
        Err(e) => eprintln!("创建目录失败: {}", e),
    }
    

    let save_path = Path::new(download_dir).join(format!("{}.jpg", file_name));
    println!("正在下载: {}", image_url);
    let response = client
        .get(image_url)
        .send()
        .await
        .map_err(|e| format!("请求失败: {}", e))?;
    let bytes = response
        .bytes()
        .await
        .map_err(|e| format!("读取数据失败: {}", e))?;
    fs::write(save_path, &bytes)
        .map_err(|e| format!("写入文件失败: {}", e))?;

    print!("{}{}", file_name, image_url);
    Ok(())
}


fn extract_image_id(url: &str) -> Option<&str> {
    // 1. 找到 "/sz_mmbiz_jpg/" 之后的部分
    let prefix = "/sz_mmbiz_jpg/";
    let start = url.find(prefix)? + prefix.len();
    // 2. 找到接下来的 "/" 或 "?"，作为结束位置
    let end = url[start..]
        .find(|c| c == '/' || c == '?')
        .map(|pos| start + pos)
        .unwrap_or(url.len());
    Some(&url[start..end])
}

fn clean_js_to_json(input: &str) -> String {
    // 修复键名无引号的问题（如 width: → "width":）
    let re_keys = Regex::new(r"([{,]\s*)([a-zA-Z_][a-zA-Z0-9_]*)(\s*:)").unwrap();
    let fixed_keys = re_keys.replace_all(input, r#"$1"$2"$3"#);

    // 修复单引号字符串（如 '960' → "960"）
    let re_quotes = Regex::new(r#"'([^']*)'"#).unwrap();
    let fixed_quotes = re_quotes.replace_all(&fixed_keys, r#""$1""#);

    // 修复 JS 表达式（如 'true' === 'true' → true, '960' * 1 → 960）
    let re_bool_expr = Regex::new(r#""true"\s*===\s*"true""#).unwrap();
    let fixed_bool = re_bool_expr.replace_all(&fixed_quotes, "true");

    let re_num_expr = Regex::new(r#""(\d+\.?\d*)"\s*\*\s*1"#).unwrap();
    let fixed_nums = re_num_expr.replace_all(&fixed_bool, "$1");
    
    let fixed = fixed_nums.replace(r#"\x26amp;amp;"#, "&");
    let re = Regex::new(r#",\s*([}\]])"#).unwrap();
    let fixed_re = re.replace_all(&fixed, "$1").to_string();

    fixed_re.to_string()
}

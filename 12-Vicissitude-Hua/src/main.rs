mod utils;
mod public;
use utils::strings_utils::process_url;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let url: &'static str = "https://mp.weixin.qq.com/s/XrIIfZYVOLvDzISpRjVzbg";
    // let url = "https://www.douyin.com/user/MS4wLjABAAAAXn-GyjbmW_K5tkt58dhYKUgOGmxCYjkUHozRkIHBcO0?from_tab_name=main";
    
    // ✅ 推荐方式：用 ? 代替 unwrap
    let result = process_url(url.to_string()).await?;
    println!("处理成功: {}", result);
    
    Ok(())
}

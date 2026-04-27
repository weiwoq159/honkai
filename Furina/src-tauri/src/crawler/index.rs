use crate::crawler::weibo_crawler::fetch_weibo_data;
use crate::crawler::weixin_crawler::fetch_weixin_data;
use crate::structs::index::SResponse;
use reqwest::Client;
use serde_json::Value;
use url::Url;

#[tauri::command]
pub async fn parse_url(
    app_handle: tauri::AppHandle,
    url: String,
) -> Result<SResponse<Value>, String> {
    let client = Client::new();
    let weibo_cookie = "SCF=AqbtfbllJSs6d_8kRS0uPtNWCY4uFOH3v4pUtTQz9rUZ_NlmCRKLlQphKOsAKR9P0PhFz1UBhqTJajk1TgJeizs.; SUB=_2A25FhxCyDeRhGeVH7VAR8i3NyzmIHXVm_Sx6rDV8PUNbmtB-LWyikW9NTynLr5kjVSUvjKz5-tga93kGM2Jzg4Aj; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9W5dee3IizpKGyTwcdLCdkMw5NHD95Q01KqEehz0eK5fWs4DqcjCKPLCqgLj9NHVi--Xi-zRi-zc; ALF=02_1756032482; _s_tentry=passport.weibo.com; Apache=4449539679043.53.1753440485487; SINAGLOBAL=4449539679043.53.1753440485487; ULV=1753440485601:1:1:1:4449539679043.53.1753440485487:; WBPSESS=u3cyzfM6DCx6pdS5XFnW9V2YVwlDJACs-nqmvsiPyQEmwMSCiSUpFXpPqjpCMZeaFNTR64D58JC3mpRBxoDIKln5kLNaG_0bSzRtBLlz-fV4v-ZSXBiUODJC4Ye9vplo7F-jV2u0-jmBu0ccR1THYw==";
    let parsed_url = match Url::parse(&url) {
        Ok(url) => url,
        Err(err) => return Err(format!("URL 解析失败: {}", err)),
    };
    
    match parsed_url.host_str() {
        Some(host) if host.contains("weixin.qq") => {
            fetch_weixin_data(&app_handle, &client, &parsed_url).await
        }
        Some(host) if host.contains("weibo.com") => {
            fetch_weibo_data(&app_handle, &client, &parsed_url, weibo_cookie).await
        }
        Some(_) => Err("不支持的域名".to_string()),
        None => Err("URL 中没有有效的域名".to_string()),
    }
}

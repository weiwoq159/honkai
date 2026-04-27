use crate::structs::index::types::OpenFileDialog;
use crate::structs::index::{AppConfig, SResponse};
use reqwest::header::{HeaderMap, HeaderValue, REFERER, USER_AGENT};
use reqwest::Client;
use std::path::Path;
use std::time::{SystemTime, UNIX_EPOCH};
use std::{fs, vec};
use tauri::{AppHandle, Manager};
use tauri_plugin_dialog::{DialogExt, FilePath};
use tauri_plugin_fs::FsExt;
use tokio::io::AsyncWriteExt;

#[tauri::command]
pub async fn open_file_dialog(app: AppHandle) -> Result<SResponse<OpenFileDialog>, String> {
    let file_path = app
        .dialog()
        .file()
        .blocking_pick_folder()
        .ok_or("未选择文件夹")?;
    let folder_path = match file_path {
        FilePath::Path(p) => p.into_os_string(),
        FilePath::Url(_) => return Err("暂不支持 URL 类型路径".into()),
    };
    return Ok(SResponse::success(OpenFileDialog {
        current_page: folder_path.into_string().unwrap(),
    }));
}

pub fn load_config() -> AppConfig {
    let content =
        fs::read_to_string(r"D:\work\mq\Honkai\11-Stars-Griseo\src-tauri\src\constant\config.json")
            .expect("配置文件读取失败");
    serde_json::from_str(&content).expect("配置文件解析失败")
}

pub fn build_headers(config: &AppConfig) -> HeaderMap {
    let mut headers = HeaderMap::new();

    headers.insert(
        USER_AGENT,
        HeaderValue::from_str(&config.user_agent).unwrap(),
    );
    headers.insert(REFERER, HeaderValue::from_str(&config.referer).unwrap());
    headers.insert(
        "X-Xsrf-Token",
        HeaderValue::from_static("BbXL1VUIzKqMWdpDAcdcGfDE"),
    );
    headers.insert("Cookie", HeaderValue::from_str("SINAGLOBAL=4551762982530.345.1697963624090; SCF=Aqu8i0tdUNxw0FABmUxleyQsHkRwO4oz-t6AdaSlv618l_BPHJrz2fHahnBaKNMry7K8GeXwuIr1zCwUevnCwI0.; ULV=1749631410949:27:2:2:1388342092712.1204.1749631410871:1749574690263; _qimei_uuid42=1960b102c3a100619123b0ec63109a43e5c2f58099; _qimei_fingerprint=13a2077e8a5e741fa6113b51037fdc49; _qimei_i_3=4dbc2c85c40c04d8c1c4a8350f8175b5f3e8a4f8140803d1b28e295072c52839656364943989e2a49183; _qimei_h38=; _qimei_i_1=6fdd64ebc81f; XSRF-TOKEN=BbXL1VUIzKqMWdpDAcdcGfDE; WBPSESS=u3cyzfM6DCx6pdS5XFnW9V2YVwlDJACs-nqmvsiPyQEmwMSCiSUpFXpPqjpCMZeaFNTR64D58JC3mpRBxoDIKn3nbXdSutCv4iwvjDjKRKKrQ0XS40hJEM8O4y4rYCGtpCnMwhvmfClgnCss-EAZPg==; PC_TOKEN=8d00df49e6; ALF=1753954230; SUB=_2A25FZ9rmDeRhGeVH7VAR8i3NyzmIHXVmHVIurDV8PUJbkNANLU7FkW1NTynLr29Eypv3HEeFP3w9c7lnuP_HVs0G; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9W5dee3IizpKGyTwcdLCdkMw5JpX5KMhUgL.Foe4Soz7eoepeh-2dJLoIpiSwHiyIgprUgRLxKBLBonLBoqtSINAGLOBAL=4551762982530.345.1697963624090; SCF=Aqu8i0tdUNxw0FABmUxleyQsHkRwO4oz-t6AdaSlv618l_BPHJrz2fHahnBaKNMry7K8GeXwuIr1zCwUevnCwI0.; ULV=1749631410949:27:2:2:1388342092712.1204.1749631410871:1749574690263; _qimei_uuid42=1960b102c3a100619123b0ec63109a43e5c2f58099; _qimei_fingerprint=13a2077e8a5e741fa6113b51037fdc49; _qimei_i_3=4dbc2c85c40c04d8c1c4a8350f8175b5f3e8a4f8140803d1b28e295072c52839656364943989e2a49183; _qimei_h38=; _qimei_i_1=6fdd64ebc81f; XSRF-TOKEN=BbXL1VUIzKqMWdpDAcdcGfDE; WBPSESS=u3cyzfM6DCx6pdS5XFnW9V2YVwlDJACs-nqmvsiPyQEmwMSCiSUpFXpPqjpCMZeaFNTR64D58JC3mpRBxoDIKn3nbXdSutCv4iwvjDjKRKKrQ0XS40hJEM8O4y4rYCGtpCnMwhvmfClgnCss-EAZPg==; PC_TOKEN=8d00df49e6; ALF=1753954230; SUB=_2A25FZ9rmDeRhGeVH7VAR8i3NyzmIHXVmHVIurDV8PUJbkNANLU7FkW1NTynLr29Eypv3HEeFP3w9c7lnuP_HVs0G; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9W5dee3IizpKGyTwcdLCdkMw5JpX5KMhUgL.Foe4Soz7eoepeh-2dJLoIpiSwHiyIgprUgRLxKBLBonLBoqt").unwrap());
    headers
}

pub fn build_weixin_headers(config: &AppConfig) -> HeaderMap {
    let mut headers = HeaderMap::new();
    headers.insert(
        REFERER,
        HeaderValue::from_str(&config.weixin_referer).unwrap(),
    );
    headers
}

#[tauri::command]
pub async fn download_file(
    app_handle: AppHandle,
    folder_path: String,
    image_list: Vec<String>,
    image_type: String,
    user_name: String,
    origin_url: String,
) -> Result<SResponse<Vec<String>>, String> {
    let _ = app_handle.fs_scope().allow_directory(&folder_path, false);
    let client = Client::new();
    let target_path = format!("{}\\{}_weibo", &folder_path, &user_name);

    // 判断文件夹是否存在，不存在则尝试创建
    if !Path::new(&target_path).is_dir() {
        fs::create_dir_all(&target_path).map_err(|e| format!("创建文件夹失败: {}", e))?;
        println!("文件夹不存在，已创建");
    } else {
        println!("文件夹已存在");
    }
    println!("准备下载 {} 张图片，类型：{}", image_list.len(), image_type);

    let config = load_config();
    let mut saved_files = Vec::new();

    for image_url in &image_list {
        let file_name = match get_filename_without_extension(&image_url) {
            Some(filename) => filename,
            None => {
                let start = SystemTime::now();
                let since_epoch = start.duration_since(UNIX_EPOCH).unwrap();
                since_epoch.as_millis().to_string()
            }
        };
        println!("{}", file_name);
        let resp = client
            .get(image_url)
            .headers(if origin_url == "weibo" {
                build_headers(&config)
            } else {
                build_weixin_headers(&config)
            })
            .send()
            .await
            .unwrap();

        let bytes = resp
            .bytes()
            .await
            .map_err(|e| format!("读取数据失败: {}", e))?;
        // 写入文件
        let mut file =
            tokio::fs::File::create(format!("{}\\{}.{}", &target_path, file_name, image_type))
                .await
                .map_err(|e| format!("创建文件失败: {}", e))?;

        file.write_all(&bytes)
            .await
            .map_err(|e| format!("写入文件失败: {}", e))?;

        println!(
            "已保存到: {}",
            format!("{}\\{}.{}", &target_path, file_name, image_type)
        );
        saved_files.push(format!("{}\\{}.{}", &target_path, file_name, image_type));
    }
    // 这里可以补充文件下载逻辑

    Ok(SResponse::success(saved_files))
}

fn get_filename_without_extension(url: &str) -> Option<String> {
    let filename = url.rsplit('/').next()?; // 先取出文件名
    let name_without_ext = filename.split('.').next()?; // 再去掉扩展名
    let final_name = name_without_ext.split('?').next()?;
    Some(final_name.to_string())
}

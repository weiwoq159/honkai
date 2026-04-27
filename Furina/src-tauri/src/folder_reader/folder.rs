use crate::{ structs::index::SResponse};
use serde_json::{json, Value};
use std::{
    fs::{self, read_dir},
    path::{Path, PathBuf},
};
use crate::structs::index::{TaskItem, TaskStatus};
use crate::services::database::insert_task_list;
use tauri::AppHandle;
use chrono::Utc;
use walkdir::WalkDir;
use infer;

const IMAGE_EXTS: [&str; 6] = ["jpg", "jpeg", "png", "webp", "gif", "avif"];

/// 判断文件是否为图片
fn is_image_file(path: &Path) -> bool {
    path.extension()
        .and_then(|ext| ext.to_str())
        .map(|ext| IMAGE_EXTS.contains(&ext.to_ascii_lowercase().as_str()))
        .unwrap_or(false)
}

/// 构造本地资源映射 URL
fn to_asset_url(path: &Path) -> String {
    format!(
        "http://asset.localhost/{}",
        path.display().to_string().replace('\\', "/")
    )
}

#[tauri::command]
pub async fn get_images_in_folder(
    _app_handle: AppHandle,
    folder_path: String,
) -> Result<SResponse<Value>, String> {
    let folder = PathBuf::from(&folder_path);

    if !folder.is_dir() {
        return Err(format!("目录不存在或不是有效文件夹: {}", folder.display()));
    }

    let entries = read_dir(&folder).map_err(|e| format!("读取目录失败: {}", e))?;

    let image_urls = entries
        .filter_map(|entry| {
            let entry = entry.ok()?;
            let path = entry.path();

            if is_image_file(&path) {
                let url = to_asset_url(&path);
                Some(json!({
                    "url": url,
                    "preview_url": url,
                }))
            } else {
                None
            }
        })
        .collect::<Vec<_>>();

    Ok(SResponse::success(json!({
        "folder_path": folder_path,
        "image_urls": image_urls
    })))
}

#[tauri::command]
pub async fn remove_file(
    _app_handle: AppHandle,
    file_path: String,
) -> Result<SResponse<Value>, String> {
    let relative_path = file_path.replace("http://asset.localhost/", "");
    let local_path = PathBuf::from(relative_path);

    if !local_path.exists() {
        return Err(format!("文件不存在：{}", local_path.display()));
    }

    fs::remove_file(&local_path).map_err(|e| format!("删除失败：{}", e))?;

    Ok(SResponse::success(json!({
        "file_path": file_path
    })))
}

pub fn is_image(path: &PathBuf) -> bool {
    if let Some(ext) = path.extension().and_then(|s| s.to_str()) {
        matches!(ext.to_lowercase().as_str(), "jpg" | "jpeg" | "png" | "bmp" | "webp")
    } else {
        false
    }
  }

pub fn collect_images_recursively(dir: &Path, result: &mut Vec<PathBuf>) {
    if let Ok(entries) = fs::read_dir(dir) {
        for entry in entries.flatten() {
            let path = entry.path();
            if path.is_dir() {
                collect_images_recursively(&path, result);
            } else if is_image(&path) {
                result.push(path);
            }
        }
    }
    }

#[tauri::command]
pub async fn deduplicate_images(
    app_handle: AppHandle,
    folder_path: String,
) -> Result<SResponse<Value>, String> {
    // 读取目录 & 校验
    let now = Utc::now().naive_utc();
    let target_dir = PathBuf::from(&folder_path); 
    let mut image_paths = Vec::new();
    collect_images_recursively(&target_dir, &mut image_paths);

    let payload = TaskItem{
        task_type: "dedup".to_string(),
        folder_path: folder_path,
        status: TaskStatus::Pending,
        result_summary: None,
        error_message: None,
        progress: 0,
        total: image_paths.len().try_into().unwrap(),
        created_at: now,
        updated_at: now
    };
    match insert_task_list(&app_handle, payload).await {
        Ok(task_id) => Ok(SResponse::success(json!({
            "task_id": task_id
        }))),
    
        Err(e) => {
            eprintln!("❌ 插入任务失败: {}", e);
            Err(format!("任务插入失败: {}", e))
        }
    }
    
}


#[tauri::command]
pub async fn get_all_folder(origin_path: String) -> Result<SResponse<Value>, String> {
    let mut folders = Vec::new();
    let origin_path = Path::new(&origin_path);
    let entries = match fs::read_dir(origin_path) {
        Ok(entries) => entries,
        Err(e) => {
            return Err(format!("读取目录失败: {}", e)); // 直接 return
        }
    };
    for entry in entries {
        let path = match entry {
            Ok(e) => e.path(),
            Err(e) => {
                eprintln!("读取目录项失败: {}", e);
                continue;
            }
        };
        let folder_name = path
            .file_name()
            .and_then(|s| s.to_str())
            .unwrap_or("未知文件夹");
        if path.is_dir() {
            folders.push(json!({
                "folder_path": path,
                "folder_name": folder_name
            }));
        }
    }
    Ok(SResponse::success(json!({
        "folder_list": folders
    })))
}

#[tauri::command]
pub async fn move_file(origin_path: String, target_path: String) -> Result<SResponse<Value>, String> {
    let prefix = "http://asset.localhost/";

    let local_path = origin_path.strip_prefix(prefix)
    .unwrap_or(&origin_path); // 如果没有前缀就原样返回
    let origin = Path::new(&local_path);
    let target_dir = Path::new(&target_path);

    // 检查源文件是否存在
    if !origin.exists() {
        return Err(format!("源文件不存在: {}", origin_path));
    }

    if !origin.is_file() {
        return Err(format!("源路径不是一个文件: {}", origin_path));
    }

    // 提取源文件名
    let file_name = match origin.file_name().and_then(|f| f.to_str()) {
        Some(name) => name,
        None => return Err("无法提取文件名".to_string()),
    };

    // 构造完整目标路径
    let target_full_path: PathBuf = target_dir.join(file_name);

    // 创建目标文件夹（如果不存在）
    if let Some(parent) = target_full_path.parent() {
        if let Err(e) = fs::create_dir_all(parent) {
            return Err(format!("创建目标目录失败: {}", e));
        }
    }

    // 执行移动操作
    if let Err(e) = fs::rename(&origin, &target_full_path) {
        return Err(format!("移动文件失败: {}", e));
    }

    // 返回响应
    Ok(SResponse::success(json!({
        "origin_path": origin.display().to_string(),
        "target_path": target_full_path.display().to_string(),
    })))
}
#[tauri::command]
pub async fn make_folder(origin_path: String, folder_name: String) -> Result<SResponse<Value>, String> {
    let new_folder_path = Path::new(&origin_path).join(&folder_name);
    if new_folder_path.exists() {
        return Err(format!("文件夹已存在: {}", new_folder_path.display()));
    }if let Err(e) = fs::create_dir_all(&new_folder_path) {
        return Err(format!("创建文件夹失败: {}", e));
    }
    Ok(SResponse::success(json!({
        "folder_path": new_folder_path.display().to_string()
    })))
}


#[tauri::command]
pub async fn reset_folder_images(
    app_handle: AppHandle,
    folder_path: String,
) -> Result<SResponse<Value>, String> {
    let root = PathBuf::from(&folder_path);

    // 可选：你可以在这里做一些文件夹校验，比如是否存在或是文件夹等
    if !root.exists() || !root.is_dir() {
        return Err("指定路径不存在或不是文件夹".into());
    }
    for entry in WalkDir::new(&root)
        .into_iter()
        .filter_map(Result::ok)
        .filter(|e| e.file_type().is_file())
    {
        let path = entry.path();
        let content = fs::read(path).unwrap();
        
        // 使用 infer 检测真实类型
        if let Some(kind) = infer::get(&content) {
            if kind.mime_type().starts_with("image/") {
                let correct_ext = kind.extension();
                let current_ext = path.extension().and_then(|s| s.to_str()).unwrap_or("").to_lowercase();

                if current_ext != correct_ext {
                    let new_path = path.with_extension(correct_ext);
                    println!("🛠️ 修正后缀: {} → {}", path.display(), new_path.display());
                    let _ = fs::rename(path, new_path).map_err(|e| e.to_string());
                }
            }
        }
    }

    println!("✅ 扫描完毕。");
    get_images_in_folder(app_handle, folder_path).await
}
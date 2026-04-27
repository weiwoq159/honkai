use crate::structs::index::types::SImageList;
use crate::structs::index::SResponse;

#[tauri::command]
pub async fn fetch_folder_image(
    current_page: String,
) -> Result<SResponse<SImageList>, SResponse<String>> {
    // 检查目录是否存在
    if !std::path::Path::new(&current_page).exists() {
        return Err(SResponse::<String>::error(
            404,
            format!("目录不存在: {}", current_page),
        ));
    }

    // 读取目录内容
    let entries = std::fs::read_dir(&current_page)
        .map_err(|e| SResponse::<String>::error(500, format!("读取目录失败: {}", e)))?;

    // 收集图片文件
    let image_urls = entries
        .filter_map(|entry| {
            let entry = entry.ok()?;
            let path = entry.path();

            // 检查文件扩展名是否为图片格式
            path.extension()
                .and_then(|ext| ext.to_str())
                .filter(|ext| {
                    ["jpg", "jpeg", "png", "webp", "gif"]
                        .contains(&ext.to_ascii_lowercase().as_str())
                })
                .map(|_| format!("http://asset.localhost/{}", path.display()))
        })
        .collect::<Vec<_>>();

    // 返回结果
    Ok(SResponse::success(SImageList {
        current_page,
        image_list: image_urls,
    }))
}

#[tauri::command]
pub async fn remove_file(image_url: String) -> Result<String, String> {
    let img_url = image_url.replace("http://asset.localhost/", "");
    if !std::path::Path::new(&img_url).exists() {
        return Err(format!("文件不存在：{}", img_url));
    }
    // 尝试删除文件
    match std::fs::remove_file(img_url) {
        Ok(_) => Ok("删除成功".to_string()),
        Err(e) => Err(format!("删除失败：{}", e)),
    }
}

use crate::structs::index::TaskStatus;
use crate::structs::index::{MediaItem, MyState, SResponse, SelectTaskItem, TaskItem, TaskResultItem, SelectTaskResultItem, UserFrom};
use serde_json::{json, Value};
use sqlx::sqlite::SqlitePoolOptions;
use sqlx::Row;
use std::collections::HashSet;
use std::path::Path;
use tauri::AppHandle;
use tauri::Manager;
use tauri_plugin_sql::Migration;
use chrono::Utc;

pub fn run_migrations(db_path: &str, migrations: &[Migration]) -> Result<(), sqlx::Error> {
    let rt = tokio::runtime::Runtime::new().unwrap();
    rt.block_on(async {
        let pool = SqlitePoolOptions::new()
            .max_connections(5)
            .connect(db_path)
            .await?;

        for migration in migrations {
            sqlx::query(migration.sql).execute(&pool).await?;
        }

        Ok(())
    })
}

pub fn create_sqlite_db_url(db_file_path: &str) -> String {
    if let Some(parent_dir) = Path::new(db_file_path).parent() {
        if !parent_dir.exists() {
            let _ = std::fs::create_dir_all(parent_dir);
        }
    }

    if !Path::new(db_file_path).exists() {
        let _ = std::fs::File::create(db_file_path);
    }

    format!("sqlite:{}", db_file_path)
}

pub async fn update_media_item(
    app_handle: &AppHandle,
    fsid: &str,
    download_url: &str,
) -> Result<(), String> {
    let state = app_handle
        .try_state::<MyState>()
        .ok_or_else(|| "MyState 尚未注册".to_string())?;
    let pool = &state.pool;
    let query = r#"
        UPDATE media_list
        SET download_url = ?
        WHERE fsid = ? AND is_deleted = 0
    "#;
    sqlx::query(query)
        .bind(download_url) // 绑定新的 download_url
        .bind(fsid) // 绑定 fsid
        .execute(pool) // 执行更新操作
        .await
        .map_err(|e| format!("更新失败: {}", e))?;

    Ok(())
}
pub async fn insert_media_item(app_handle: &AppHandle, item: MediaItem) -> Result<u64, String> {
    let state = app_handle
        .try_state::<MyState>()
        .ok_or_else(|| "MyState 尚未注册".to_string())?;
    let pool = &state.pool;
    let sql = r#"
        INSERT INTO media_list (
            preview_url, url, media_type, format, blog_id, user_id, created_at, origin_from, is_deleted, file_name, md5_code, download_url
        ) VALUES (
            ?1, ?2, ?3, ?4, ?5, ?6, ?7, ?8, ?9, ?10, ?11, ?12
        )
        ON CONFLICT(url) DO NOTHING;
    "#;
    let result = sqlx::query(sql)
        .bind(item.preview_url)
        .bind(item.url)
        .bind(item.media_type.unwrap_or_else(|| "image".to_string()))
        .bind(item.format)
        .bind(item.blog_id)
        .bind(item.user_id)
        .bind(item.created_at)
        .bind(item.origin_from)
        .bind(item.is_deleted)
        .bind(item.file_name)
        .bind(item.md5_code)
        .bind(item.download_url)
        .execute(pool)
        .await
        .map_err(|e| format!("插入失败: {}", e))?;

    Ok(result.rows_affected())
}
pub async fn select_md5_set_by_from(
    app_handle: &AppHandle,
    from: &str,
) -> Result<HashSet<String>, String> {
    let state = app_handle
        .try_state::<MyState>()
        .ok_or_else(|| "MyState 尚未注册".to_string())?;

    let pool = &state.pool;
    let sql: String = format!(
        r#"SELECT md5_code FROM media_list WHERE origin_from = '{}'"#,
        from
    );
    let rows = sqlx::query(&sql)
        .bind(from)
        .fetch_all(pool)
        .await
        .map_err(|e| format!("查询失败: {}", e))?;

    let md5_set: HashSet<String> = rows
        .into_iter()
        .filter_map(|row| row.try_get::<String, _>("md5_code").ok())
        .collect();

    Ok(md5_set)
}

pub async fn select_media_item_by_from(
    app_handle: &AppHandle,
    origin_from: &str,
    include_empty_download_url: bool, // 使用 bool 类型的参数来控制是否加上 download_url 判空条件
) -> Result<Value, String> {
    let state = app_handle
        .try_state::<MyState>()
        .ok_or_else(|| "MyState 尚未注册".to_string())?;

    let pool = &state.pool;

    // 根据 include_empty_download_url 的值来动态构建查询条件
    let sql = if include_empty_download_url {
        // 如果需要包含 download_url 为空的条件
        format!(
            r#"SELECT * FROM media_list WHERE "origin_from" = '{}' AND is_deleted = 0 AND ("download_url" IS NULL OR "download_url" = '') ORDER BY id ASC"#,
            origin_from
        )
    } else {
        // 如果不需要，按照原来的查询条件
        format!(
            r#"SELECT * FROM media_list WHERE "origin_from" = '{}' AND is_deleted = 0 ORDER BY id ASC"#,
            origin_from
        )
    };

    // 执行查询
    let rows: Vec<MediaItem> = sqlx::query_as(&sql)
        .fetch_all(pool)
        .await
        .map_err(|e| format!("查询失败: {}", e))?;

    Ok(json!(rows))
}

#[tauri::command]
pub async fn remove_media_item_by_url(
    app_handle: AppHandle,
    url: String,
) -> Result<SResponse<Value>, String> {
    let state = app_handle
        .try_state::<MyState>()
        .ok_or_else(|| "MyState 尚未注册".to_string())?;

    let pool = &state.pool;
    let sql = r#"
        UPDATE media_list
        SET is_deleted = 1
        WHERE url = ?1
    "#;

    let result = sqlx::query(sql)
        .bind(&url)
        .execute(pool)
        .await
        .map_err(|e| format!("删除失败: {}", e))?;

    if result.rows_affected() == 0 {
        return Err(format!("未找到 URL 为 {} 的记录", url));
    }

    Ok(SResponse {
        status: 200,
        message: "删除成功~~".to_string(),
        data: json!({
            "url": url
        }),
    })
}

pub async fn insert_task_list(app_handle: &AppHandle, task_item: TaskItem) -> Result<u64, String> {
    let state = app_handle
        .try_state::<MyState>()
        .ok_or_else(|| "MyState 尚未注册".to_string())?;
    let pool = &state.pool;
    let sql = r#"
        INSERT INTO task_list (
            task_type, folder_path, status, progress, total, result_summary, error_message, created_at, updated_at 
        ) VALUES (
            ?1, ?2, ?3, ?4, ?5, ?6, ?7, ?8, ?9
        )
    "#;
    let result = sqlx::query(sql)
        .bind(task_item.task_type)
        .bind(task_item.folder_path)
        .bind(task_item.status)
        .bind(task_item.progress)
        .bind(task_item.total)
        .bind(task_item.result_summary)
        .bind(task_item.error_message)
        .bind(task_item.created_at.format("%Y-%m-%d %H:%M:%S").to_string())
        .bind(task_item.updated_at.format("%Y-%m-%d %H:%M:%S").to_string())
        .execute(pool)
        .await
        .map_err(|e| format!("插入失败: {}", e))?;
    let task_id = result.last_insert_rowid(); // ✅ 这是插入后的任务 ID

    Ok(task_id as u64)
}

pub async fn select_task_list(app_handle: &AppHandle) -> Result<Vec<SelectTaskItem>, String> {
    let state = app_handle
        .try_state::<MyState>()
        .ok_or_else(|| "MyState 尚未注册".to_string())?;
    let pool = &state.pool;
    let sql = r#"
        SELECT * FROM task_list WHERE status = 'pending' ORDER BY id ASC
    "#;
    let rows = sqlx::query_as::<_, SelectTaskItem>(sql)
        .fetch_all(pool)
        .await
        .map_err(|e| format!("查询失败: {}", e))?;
    Ok(rows)
}

#[tauri::command]
pub async fn select_all_task_list(app_handle: AppHandle) -> Result<Vec<SelectTaskItem>, String> {
    let state = app_handle
        .try_state::<MyState>()
        .ok_or_else(|| "MyState 尚未注册".to_string())?;
    let pool = &state.pool;
    let sql = r#"
        SELECT * FROM task_list ORDER BY id ASC
    "#;
    let rows = sqlx::query_as::<_, SelectTaskItem>(sql)
        .fetch_all(pool)
        .await
        .map_err(|e| format!("查询失败: {}", e))?;
    Ok(rows)
}


#[tauri::command]
pub async fn select_all_task_result_list(
    app_handle: AppHandle,
    task_id: String,
) -> Result<Vec<SelectTaskResultItem>, String> {
    let state = app_handle
        .try_state::<MyState>()
        .ok_or_else(|| "MyState 尚未注册".to_string())?;
    let pool = &state.pool;

    let sql = r#"
        SELECT * FROM task_result_list WHERE task_id = ? ORDER BY id ASC
    "#;

    let rows = sqlx::query_as::<_, SelectTaskResultItem>(sql)
        .bind(task_id)
        .fetch_all(pool)
        .await
        .map_err(|e| format!("查询失败: {}", e))?;

    Ok(rows)
}

pub async fn check_if_processing(app_handle: &AppHandle) -> Result<bool, String> {
    let state = app_handle
        .try_state::<MyState>()
        .ok_or_else(|| "MyState 尚未注册".to_string())?;
    let pool = &state.pool;

    let row = sqlx::query_scalar::<_, i64>(
        "SELECT COUNT(*) FROM task_list WHERE status = 'processing'"
    )
    .fetch_one(pool)
    .await
    .map_err(|e| format!("查询 processing 任务失败: {}", e))?;

    Ok(row > 0)
}

pub async fn update_task_status(
    app_handle: &AppHandle,
    task_id: i64,
    new_status: TaskStatus,
) -> Result<u64, String> {
    let state = app_handle
        .try_state::<MyState>()
        .ok_or_else(|| "MyState 尚未注册".to_string())?;
    let pool = &state.pool;
    let current_time = Utc::now().naive_utc();
    let sql = r#"
        UPDATE task_list
        SET status = ?, updated_at = ?
        WHERE id = ?
    "#;

    let result = sqlx::query(sql)
        .bind(new_status)
        .bind(current_time.format("%Y-%m-%d %H:%M:%S").to_string())
        .bind(task_id)
        .execute(pool)
        .await
        .map_err(|e| format!("更新任务状态失败: {}", e))?;

    Ok(result.rows_affected())
}
pub async fn update_task_progress(
    app_handle: &AppHandle,
    task_id: i64,
    progress: u128,
) -> Result<u64, String> {
    println!("{}", task_id);
    let state = app_handle
        .try_state::<MyState>()
        .ok_or_else(|| "MyState 尚未注册".to_string())?;
    let pool = &state.pool;
    let current_time = Utc::now().naive_utc();
    let sql = r#"
        UPDATE task_list
        SET progress = ?, updated_at = ?
        WHERE id = ?
    "#;

    let result = sqlx::query(sql)
        .bind(progress.to_string())
        .bind(current_time.format("%Y-%m-%d %H:%M:%S").to_string())
        .bind(task_id)
        .execute(pool)
        .await
        .map_err(|e| format!("更新任务状态失败: {}", e))?;

    Ok(result.rows_affected())
}

pub async fn update_task_progress_pending(
    app_handle: &AppHandle,
) -> Result<u64, String> {
    println!("状态重置开始");

    let state = app_handle
        .try_state::<MyState>()
        .ok_or_else(|| "MyState 尚未注册".to_string())?;
    let pool = &state.pool;
    let sql = r#"
        UPDATE task_list SET status = 'pending' WHERE status = 'processing'
    "#;

    let result = sqlx::query(sql)
        .execute(pool)
        .await
        .map_err(|e| format!("更新任务状态失败: {}", e))?;
    println!("状态重置成功");
    Ok(result.rows_affected())
}

pub async fn update_task_result(
    app_handle: &AppHandle,
    task_id: i64,
    task_result: String,
) -> Result<u64, String> {
    let state = app_handle
        .try_state::<MyState>()
        .ok_or_else(|| "MyState 尚未注册".to_string())?;
    let pool = &state.pool;
    let current_time = Utc::now().naive_utc();
    let sql = r#"
        UPDATE task_list
        SET result_summary = ?, updated_at = ?
        WHERE id = ?
    "#;

    let result = sqlx::query(sql)
        .bind(task_result)
        .bind(current_time.format("%Y-%m-%d %H:%M:%S").to_string())
        .bind(task_id)
        .execute(pool)
        .await
        .map_err(|e| format!("更新任务状态失败: {}", e))?;

    Ok(result.rows_affected())
}

pub async fn insert_task_result_list(app_handle: &AppHandle, task_result_item: TaskResultItem) -> Result<u64, String> {
    println!("charu");
    let state = app_handle
        .try_state::<MyState>()
        .ok_or_else(|| "MyState 尚未注册".to_string())?;
    let pool = &state.pool;
    let sql = r#"
        INSERT INTO task_result_list (task_id, result)
        VALUES (?1, ?2)
        ON CONFLICT(task_id) DO UPDATE SET
            result = excluded.result,
            created_at = CURRENT_TIMESTAMP
    "#;
    let result = sqlx::query(sql)
        .bind(task_result_item.task_id)
        .bind(task_result_item.result)
        .execute(pool)
        .await
        .map_err(|e| format!("插入失败: {}", e))?;
    let task_id = result.last_insert_rowid(); // ✅ 这是插入后的任务 ID

    Ok(task_id as u64)
}


// 插入用户表
pub async fn insert_user_table(app_handle: &AppHandle, user_name: &str, user_id: &str, user_from: UserFrom) -> Result<u64, String> {
    let state = app_handle
        .try_state::<MyState>()
        .ok_or_else(|| "MyState 尚未注册".to_string())?;
    let pool = &state.pool;
    let platform_id_column = match user_from {
        UserFrom::Weibo => "weibo_id",
        UserFrom::Douyin => "douyin_id",
        UserFrom::RedNote => "red_note_id",
        UserFrom::Bilibili => "bilibili_id",
    };
    
    let sql = format!(
        "INSERT INTO users_table (user_name, {0}) VALUES(?1, ?2) \
         ON CONFLICT(user_name) DO UPDATE SET {0} = excluded.{0};",
        platform_id_column
    );
    print!("{}", sql);
    let result = sqlx::query(&sql)
        .bind(user_name)
        .bind(user_id)
        .execute(pool)
        .await
        .map_err(|e| format!("插入失败: {}", e))?;
    let task_id = result.last_insert_rowid(); // ✅ 这是插入后的任务 ID

    Ok(task_id as u64)
}
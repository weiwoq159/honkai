use crate::structs::index::{BlogParams, MyState, WeiboUrl};
use sqlx::sqlite::SqlitePoolOptions;
use sqlx::Row;
use std::path::Path;
use tauri::AppHandle;
use tauri::Manager;
use tauri_plugin_sql::Migration;

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

pub async fn insert_user(
    app_handle: &AppHandle,
    user_name: &str,
    column_name: &str, // 比如 "weibo_id"、"bilibili_id"
    column_value: &str,
) {
    println!(
        "user_name: {}, column: {}, value: {}",
        user_name, column_name, column_value
    );

    let state = app_handle.state::<MyState>();
    let pool = &state.pool;

    // 动态拼接 SQL
    let sql = format!(
        "
        INSERT INTO users_table (user_name, {col})
        VALUES (?, ?)
        ON CONFLICT(user_name) DO UPDATE SET {col} = excluded.{col};
        ",
        col = column_name
    );

    let result = sqlx::query(&sql)
        .bind(user_name)
        .bind(column_value)
        .execute(pool)
        .await;

    println!("{:?}", result);

    match result {
        Ok(_) => println!("插入或更新用户成功"),
        Err(e) => println!("插入或更新用户失败: {}", e),
    }
}
// let sql = "
//     INSERT INTO weibo_list (
//         blog_id, user_id, text, text_raw, create_time, url, type
//     ) VALUES (?, ?, ?, ?, ?, ?, ?)
//     ON CONFLICT(blog_id) DO UPDATE SET
//         user_id = excluded.user_id,
//         text = excluded.text,
//         text_raw = excluded.text_raw,
//         create_time = excluded.create_time,
//         url = excluded.url,
//         type = excluded.type;
// ";

pub async fn insert_blog_item(
    app_handle: &AppHandle,
    params: BlogParams<'_>,
) -> Result<bool, String> {
    let state = app_handle.state::<MyState>();
    let pool = &state.pool;

    let sql = "
        INSERT INTO weibo_list (
            blog_id, user_id, text, text_raw, create_time, url, preview_url, weibo_type
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(blog_id) DO NOTHING;
    ";

    let result = sqlx::query(sql)
        .bind(params.blog_id)
        .bind(params.user_id)
        .bind(params.text)
        .bind(params.text_raw)
        .bind(params.create_time)
        .bind(params.url)
        .bind(params.preview_url)
        .bind(params.blog_type)
        .execute(pool)
        .await
        .map_err(|e| format!("插入或更新失败: {}", e))?;

    // rows_affected 返回 1 说明插入了新数据，返回 0 说明已存在跳过
    Ok(result.rows_affected() == 1)
}

pub async fn select_url_from_weibo(app_handle: &AppHandle, uid: &str) -> Result<WeiboUrl, String> {
    let state = app_handle.state::<MyState>();
    let pool = &state.pool;
    let sql = "
        SELECT url, preview_url FROM weibo_list WHERE user_id = ? ;
    ";
    let result = sqlx::query(sql).bind(uid).fetch_all(pool).await;

    match result {
        Ok(rows) => {
            let mut urls = Vec::new();
            let mut preview_url = Vec::new();

            for row in rows {
                let url_str: &str = row.try_get("url").unwrap_or("");
                if !url_str.is_empty() {
                    // 按逗号分割，并去掉两边多余空格
                    let parts = url_str
                        .split(',')
                        .map(|s| s.trim().to_string())
                        .filter(|s| !s.is_empty());

                    urls.extend(parts);
                }
                let preview_url_str = row.try_get("preview_url").unwrap_or("");
                if !preview_url_str.is_empty() {
                    // 按逗号分割，并去掉两边多余空格
                    let parts = preview_url_str
                        .split(',')
                        .map(|s| s.trim().to_string())
                        .filter(|s| !s.is_empty());

                    preview_url.extend(parts);
                }
            }
            Ok(WeiboUrl {
                url: urls,
                preview_url: preview_url,
            })
        }
        Err(e) => Err(format!("查询失败: {}", e)),
    }
}

pub async fn select_user_by_weibo_id(
    app_handle: &AppHandle,
    uid: &str,
) -> Result<(String, String), String> {
    println!("{}", uid);
    let state = app_handle.state::<MyState>();
    let pool = &state.pool;

    let sql = "
        SELECT user_name, weibo_id FROM users_table WHERE weibo_id = ?;
    ";

    match sqlx::query(sql).bind(uid).fetch_one(pool).await {
        Ok(row) => {
            let username: String = row.try_get("user_name").unwrap_or_default();
            let weibo_id: String = row.try_get("weibo_id").unwrap_or_default();
            Ok((username, weibo_id))
        }
        Err(e) => Err(format!("查询失败: {}", e)),
    }
}

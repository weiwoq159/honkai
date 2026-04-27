pub mod crawler;
pub mod folder_manage;
pub mod structs;
pub mod utils;

use crawler::parse_url::parse_input_url;
use folder_manage::index::{fetch_folder_image, remove_file};
use sqlx::SqlitePool;
use structs::index::MyState;
use tauri_plugin_sql::{Migration, MigrationKind};
use utils::database::{create_sqlite_db_url, run_migrations};
use utils::utils::{download_file, open_file_dialog};

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    let migrations = vec![
        Migration {
            version: 1,
            description: "create_initial_tables",
            sql: "CREATE TABLE IF NOT EXISTS users_table (user_name TEXT PRIMARY KEY, douyin_id TEXT UNIQUE, weibo_id TEXT UNIQUE, bilibili_id TEXT UNIQUE, red_note_id TEXT UNIQUE);",
            kind: MigrationKind::Up,
        },
        Migration {
            version: 2,
            description: "create_weibo_list",
            sql: "CREATE TABLE IF NOT EXISTS weibo_list (
                blog_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                text TEXT NOT NULL,
                text_raw TEXT NOT NULL,
                create_time TEXT NOT NULL,
                url TEXT NOT NULL,
                preview_url TEXT NOT NULL,
                weibo_type TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users_table (weibo_id)
                    ON DELETE CASCADE
                    ON UPDATE RESTRICT
            );",
            kind: MigrationKind::Up,
        },
        Migration {
            version: 3,
            description: "create_config_tables",
            sql: "CREATE TABLE IF NOT EXISTS config_tables (key TEXT, value TEXT);",
            kind: MigrationKind::Up,
        },
    ];

    let db_file_path = r"D:\work\mq\Honkai\11-Stars-Griseo\sqlite\db.sqlite";
    let db_url = create_sqlite_db_url(db_file_path);

    run_migrations(db_file_path, &migrations).expect("Failed to run migrations");

    let pool = tokio::runtime::Runtime::new()
        .unwrap()
        .block_on(SqlitePool::connect(db_file_path))
        .expect("Failed to connect to DB");

    tauri::Builder::default()
        .plugin(tauri_plugin_dialog::init())
        .plugin(tauri_plugin_fs::init())
        .plugin(
            tauri_plugin_sql::Builder::default()
                .add_migrations(&db_url, migrations)
                .build(),
        )
        .manage(MyState { pool })
        .invoke_handler(tauri::generate_handler![
            open_file_dialog,
            fetch_folder_image,
            remove_file,
            parse_input_url,
            download_file
        ])
        .setup(|app| {
            if cfg!(debug_assertions) {
                app.handle().plugin(
                    tauri_plugin_log::Builder::default()
                        .level(log::LevelFilter::Info)
                        .build(),
                )?;
            }
            Ok(())
        })
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}

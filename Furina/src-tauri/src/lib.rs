pub mod crawler;
pub mod folder_reader;
pub mod services;
pub mod structs;
use crawler::index::parse_url;
use crawler::yan::fetch_yan_image_list;
use crawler::baidu_crawler::{fetch_baidu_image_list, resolve_media_list};

use folder_reader::folder::{reset_folder_images, get_images_in_folder, remove_file, deduplicate_images, get_all_folder, move_file, make_folder};
use services::database::{create_sqlite_db_url, remove_media_item_by_url, run_migrations, select_all_task_list, select_all_task_result_list};
use services::dialog::open_file_dialog;
use services::download_file::download_file;
use sqlx::SqlitePool;
use structs::index::MyState;
use tauri::Manager;
use tauri_plugin_sql::{Migration, MigrationKind};
use services::task_scheduler::run_task_scheduler;

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
        Migration {
            version: 4,
            description: "create_media_list",
            sql: r#"
                CREATE TABLE IF NOT EXISTS media_list (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    preview_url TEXT NOT NULL,
                    url TEXT NOT NULL UNIQUE,
                    blog_id TEXT,
                    user_id TEXT,
                    media_type TEXT NOT NULL DEFAULT 'image',
                    format TEXT DEFAULT NULL,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    origin_from TEXT NOT NULL,
                    is_deleted INTEGER NOT NULL DEFAULT 0,
                    file_name TEXT NOT NULL,
                    md5_code TEXT NOT NULL UNIQUE,
                    download_url TEXT,
                    FOREIGN KEY (blog_id) REFERENCES weibo_list (blog_id)
                        ON DELETE CASCADE
                        ON UPDATE CASCADE,
                    FOREIGN KEY (user_id) REFERENCES users_table (weibo_id)
                        ON DELETE CASCADE
                        ON UPDATE CASCADE
                );
            "#,
            kind: MigrationKind::Up,
        },
        
        Migration {
            version: 5,
            description: "create task list",
            sql: r#"
                CREATE TABLE IF NOT EXISTS task_list (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,      -- 任务 ID
                    task_type TEXT NOT NULL,                   -- 任务类型（如 'dedup'）
                    folder_path TEXT NOT NULL,                 -- 任务处理路径
                    status TEXT NOT NULL DEFAULT 'pending',    -- 任务状态
                    progress INTEGER DEFAULT 0,                -- 当前已处理图片数
                    total INTEGER DEFAULT 0,                   -- 总图片数
                    result_summary TEXT,                       -- 简要结果描述（如 '找到相似图组: 132 组'）
                    error_message TEXT,                        -- 错误日志
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                );
            "#,
            kind: MigrationKind::Up,
        },

        Migration {
            version: 5,
            description: "create task result list",
            sql: r#"
                CREATE TABLE IF NOT EXISTS task_result_list (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_id TEXT NOT NULL UNIQUE,
                    result TEXT NOT NULL,  -- 存储 JSON 字符串，如 [["a.png", "b.png"], ["c.png"]]
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                );
            "#,
            kind: MigrationKind::Up,
        }
    ];

    let db_file_path = r"D:\work\mq\Furina\db\db.sqlite";
    let db_url = create_sqlite_db_url(db_file_path);
    run_migrations(db_file_path, &migrations).expect("Failed to run migrations");

    let pool = tokio::runtime::Runtime::new()
        .unwrap()
        .block_on(SqlitePool::connect(db_file_path))
        .expect("Failed to connect to DB");

    tauri::Builder::default()
        .manage(MyState { pool })
        .plugin(
            tauri_plugin_sql::Builder::default()
                .add_migrations(&db_url, migrations)
                .build(),
        )
        .plugin(
            tauri_plugin_log::Builder::default()
                .level(log::LevelFilter::Info)
                .build(),
        )
        .plugin(tauri_plugin_dialog::init())
        .setup(|app| {
            let _state = app
                .app_handle()
                .try_state::<MyState>()
                .ok_or_else(|| "⚠️ MyState 尚未注册，请确保 .manage(MyState) 被调用")?;
            println!("✅ MyState 已注册");
            let app_handle = app.handle().clone();
            tauri::async_runtime::spawn(async move {
                let _ = run_task_scheduler(app_handle).await;
            });
            Ok(())
        })
        .invoke_handler(tauri::generate_handler![
            open_file_dialog,
            get_images_in_folder,
            remove_file,
            parse_url,
            download_file,
            fetch_yan_image_list,
            remove_media_item_by_url,
            fetch_baidu_image_list,
            resolve_media_list,
            deduplicate_images,
            get_all_folder,
            move_file,
            make_folder,
            select_all_task_list,
            select_all_task_result_list,
            reset_folder_images
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}

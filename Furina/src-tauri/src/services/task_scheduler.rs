use tauri::AppHandle;
use crate::services::database::{select_task_list, check_if_processing, update_task_progress_pending};
use crate::folder_reader::deduplicate::deduplicate_img;
use tokio::time::{sleep, Duration};

pub async fn run_task_scheduler(app_handle: AppHandle) -> Result<(), String> {
    println!("🟢 任务调度器已启动");
    let _ = update_task_progress_pending(&app_handle).await?;
    loop {
        // 1. 检查是否有任务在执行
        let processing_exists = check_if_processing(&app_handle).await?;
        
        if processing_exists {
            println!("⚙️ 当前已有任务正在执行，等待中...");
            sleep(Duration::from_secs(5)).await;
            continue;
        }
        // 2. 查询任务列表
        let rows = match select_task_list(&app_handle).await {
            Ok(row) => row,
            Err(_) => {
                println!("ℹ️ 当前无待处理任务");
                sleep(Duration::from_secs(5)).await;
                continue;
            }
        };

        // 3. 逐条处理
        let mut task_found = false;
        for row in &rows {
            if row.status != "pending" {
                continue;
            }
            task_found = true;

            match row.task_type.as_str() {
                "dedup" => {
                    println!("🧹 开始执行去重任务 #{}", row.id);
                    let _ = deduplicate_img(&app_handle, row).await?;
                }
                "hash" => {
                    println!("🔍 执行 hash 任务 #{}", row.id);
                    // TODO: hash 任务逻辑
                }
                other => {
                    println!("❓ 未知任务类型: {}", other);
                }
            }

            break; // 每次轮询只执行一条任务
        }

        if !task_found {
            println!("🕓 暂无 pending 任务");
        }

        // 4. 等待下一轮
        sleep(Duration::from_secs(5)).await;
    }
}

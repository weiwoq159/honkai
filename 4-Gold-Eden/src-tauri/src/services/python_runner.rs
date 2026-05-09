use std::{
    env,
    io::{BufRead, BufReader, Read, Write},
    path::{Path, PathBuf},
    process::{Command, Stdio},
    sync::{Arc, Mutex},
    thread,
};

use serde::Serialize;
use serde_json::Value;
use tauri::{AppHandle, Emitter};

use crate::commands::tool::{RunToolPayload, RunToolResult};

#[derive(Clone, Serialize)]
#[serde(rename_all = "camelCase")]
struct ToolProgressPayload {
    plugin_id: String,
    data: Value,
}

#[derive(Clone, Serialize)]
#[serde(rename_all = "camelCase")]
struct ToolLogPayload {
    plugin_id: String,
    data: String,
}

pub fn run_python_plugin(app: AppHandle, payload: RunToolPayload) -> Result<RunToolResult, String> {
    let project_dir = resolve_project_dir()?;
    let plugin_dir = resolve_plugin_dir(&project_dir, &payload.plugin_id)?;
    let python_exe = resolve_python_exe(&project_dir);
    let plugin_main = plugin_dir.join("main.py");
    let sdk_dir = project_dir.join("py-runtime").join("sdk");

    if !plugin_main.exists() {
        return Err(format!("Python 插件入口不存在：{}", plugin_main.display()));
    }

    let stdin_json =
        serde_json::to_string(&payload).map_err(|error| format!("序列化插件入参失败：{error}"))?;

    let logs: Arc<Mutex<Vec<String>>> = Arc::new(Mutex::new(Vec::new()));

    let mut command = Command::new(&python_exe);

    command
        .arg(&plugin_main)
        .current_dir(&plugin_dir)
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .env("PYTHONUNBUFFERED", "1")
        .env("PYTHONUTF8", "1")
        .env("PYTHONIOENCODING", "utf-8")
        .env("GOLD_EDEN_PROJECT_DIR", &project_dir)
        .env("GOLD_EDEN_PLUGIN_DIR", &plugin_dir)
        .env("PYTHONPATH", build_python_path(&sdk_dir, &plugin_dir));

    #[cfg(windows)]
    {
        use std::os::windows::process::CommandExt;

        const CREATE_NO_WINDOW: u32 = 0x08000000;
        command.creation_flags(CREATE_NO_WINDOW);
    }

    let mut child = command.spawn().map_err(|error| {
        format!(
            "启动 Python 插件失败：python={} plugin={} error={}",
            python_exe.display(),
            plugin_main.display(),
            error
        )
    })?;

    {
        let mut stdin = child
            .stdin
            .take()
            .ok_or_else(|| "无法打开 Python stdin".to_string())?;

        stdin
            .write_all(stdin_json.as_bytes())
            .map_err(|error| format!("写入 Python stdin 失败：{error}"))?;
    }

    let stdout = child
        .stdout
        .take()
        .ok_or_else(|| "无法读取 Python stdout".to_string())?;

    let stderr = child
        .stderr
        .take()
        .ok_or_else(|| "无法读取 Python stderr".to_string())?;

    let stdout_handle = thread::spawn(move || -> Result<String, String> {
        let mut reader = BufReader::new(stdout);
        let mut buffer = String::new();

        reader
            .read_to_string(&mut buffer)
            .map_err(|error| format!("读取 Python stdout 失败：{error}"))?;

        Ok(buffer)
    });

    let stderr_app = app.clone();
    let stderr_plugin_id = payload.plugin_id.clone();
    let stderr_logs = logs.clone();

    let stderr_handle = thread::spawn(move || {
        read_stderr_lines(stderr_app, stderr_plugin_id, stderr, stderr_logs);
    });

    let status = child
        .wait()
        .map_err(|error| format!("等待 Python 进程结束失败：{error}"))?;

    let stdout_text = stdout_handle
        .join()
        .map_err(|_| "stdout 读取线程异常退出".to_string())??;

    stderr_handle
        .join()
        .map_err(|_| "stderr 读取线程异常退出".to_string())?;

    let collected_logs = logs
        .lock()
        .map_err(|_| "读取日志缓存失败".to_string())?
        .clone();

    let stdout_trimmed = stdout_text.trim();

    if stdout_trimmed.is_empty() {
        return Ok(RunToolResult {
            success: false,
            message: if status.success() {
                "Python 插件没有输出最终 JSON".to_string()
            } else {
                format!("Python 插件执行失败，退出码：{:?}", status.code())
            },
            data: None,
            logs: collected_logs,
        });
    }

    let mut result: RunToolResult = serde_json::from_str(stdout_trimmed).map_err(|error| {
        format!(
            "解析 Python stdout 最终 JSON 失败：{}\nstdout={}",
            error, stdout_trimmed
        )
    })?;

    if !status.success() && result.success {
        result.success = false;
        result.message = format!("Python 插件异常退出，退出码：{:?}", status.code());
    }

    if result.logs.is_empty() {
        result.logs = collected_logs;
    } else {
        result.logs.extend(collected_logs);
    }

    Ok(result)
}

fn read_stderr_lines<R: Read + Send + 'static>(
    app: AppHandle,
    fallback_plugin_id: String,
    stderr: R,
    logs: Arc<Mutex<Vec<String>>>,
) {
    let reader = BufReader::new(stderr);

    for line_result in reader.lines() {
        let line = match line_result {
            Ok(value) => value,
            Err(error) => {
                let message = format!("[ERROR] 读取 Python stderr 失败：{error}");
                push_log(&logs, message.clone());
                emit_log(&app, &fallback_plugin_id, message);
                continue;
            }
        };

        let trimmed = line.trim();

        if trimmed.is_empty() {
            continue;
        }

        if let Ok(value) = serde_json::from_str::<Value>(trimmed) {
            if let Some(event_type) = value.get("type").and_then(|item| item.as_str()) {
                let plugin_id = value
                    .get("pluginId")
                    .or_else(|| value.get("plugin_id"))
                    .and_then(|item| item.as_str())
                    .unwrap_or(&fallback_plugin_id)
                    .to_string();

                match event_type {
                    "tool_progress" => {
                        let data = value.get("data").cloned().unwrap_or(Value::Null);

                        let _ = app.emit("tool-progress", ToolProgressPayload { plugin_id, data });

                        continue;
                    }

                    "tool_log" => {
                        let data = value
                            .get("data")
                            .and_then(|item| item.as_str())
                            .unwrap_or("")
                            .to_string();

                        if !data.is_empty() {
                            push_log(&logs, data.clone());
                            emit_log(&app, &plugin_id, data);
                        }

                        continue;
                    }

                    _ => {}
                }
            }
        }

        push_log(&logs, trimmed.to_string());
        emit_log(&app, &fallback_plugin_id, trimmed.to_string());
    }
}

fn emit_log(app: &AppHandle, plugin_id: &str, message: String) {
    let _ = app.emit(
        "tool-log",
        ToolLogPayload {
            plugin_id: plugin_id.to_string(),
            data: message,
        },
    );
}

fn push_log(logs: &Arc<Mutex<Vec<String>>>, message: String) {
    if let Ok(mut guard) = logs.lock() {
        guard.push(message);
    }
}

fn resolve_project_dir() -> Result<PathBuf, String> {
    if let Ok(value) = env::var("GOLD_EDEN_PROJECT_DIR") {
        let path = PathBuf::from(value);

        if path.exists() {
            return Ok(path);
        }
    }

    let manifest_dir = PathBuf::from(env!("CARGO_MANIFEST_DIR"));

    let project_dir = manifest_dir
        .parent()
        .ok_or_else(|| "无法从 CARGO_MANIFEST_DIR 推导项目根目录".to_string())?
        .to_path_buf();

    Ok(project_dir)
}

fn resolve_plugin_dir(project_dir: &Path, plugin_id: &str) -> Result<PathBuf, String> {
    let external_plugins_dir = project_dir.join("external-plugins");

    if !external_plugins_dir.exists() {
        return Err(format!(
            "external-plugins 目录不存在：{}",
            external_plugins_dir.display()
        ));
    }

    let entries = std::fs::read_dir(&external_plugins_dir).map_err(|error| {
        format!(
            "读取 external-plugins 目录失败：{}，error={}",
            external_plugins_dir.display(),
            error
        )
    })?;

    for entry_result in entries {
        let entry = entry_result.map_err(|error| format!("读取插件分类目录失败：{error}"))?;

        let category_dir = entry.path();

        if !category_dir.is_dir() {
            continue;
        }

        let plugin_dir = category_dir.join(plugin_id);

        if plugin_dir.exists() && plugin_dir.is_dir() {
            return Ok(plugin_dir);
        }
    }

    Err(format!(
        "插件目录不存在：{}\\*\\{}",
        external_plugins_dir.display(),
        plugin_id
    ))
}

fn resolve_python_exe(project_dir: &Path) -> PathBuf {
    if let Ok(value) = env::var("GOLD_EDEN_PYTHON") {
        let path = PathBuf::from(value);

        if path.exists() {
            return path;
        }
    }

    let runtime_dir = project_dir.join("py-runtime");

    #[cfg(windows)]
    {
        let candidates = [
            runtime_dir.join(".venv").join("Scripts").join("python.exe"),
            runtime_dir.join("python").join("python.exe"),
        ];

        for item in candidates {
            if item.exists() {
                return item;
            }
        }

        PathBuf::from("python")
    }

    #[cfg(not(windows))]
    {
        let candidates = [
            runtime_dir.join(".venv").join("bin").join("python"),
            runtime_dir.join("python").join("bin").join("python"),
        ];

        for item in candidates {
            if item.exists() {
                return item;
            }
        }

        PathBuf::from("python3")
    }
}

fn build_python_path(sdk_dir: &Path, plugin_dir: &Path) -> String {
    let separator = if cfg!(windows) { ";" } else { ":" };

    [
        sdk_dir.to_string_lossy().to_string(),
        plugin_dir.to_string_lossy().to_string(),
    ]
    .join(separator)
}

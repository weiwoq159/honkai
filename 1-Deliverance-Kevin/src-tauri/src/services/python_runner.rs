use std::{
    fs,
    io::{BufRead, BufReader, Read, Write},
    path::{Path, PathBuf},
    process::{Command, Stdio},
    thread,
};

use serde::{Deserialize, Serialize};
use serde_json::{json, Value};
use tauri::Emitter;

use crate::commands::tool::{RunToolPayload, RunToolResult};

#[derive(Debug, Deserialize)]
#[serde(rename_all = "camelCase")]
struct PluginManifest {
    id: String,
    name: String,
    version: String,
    runtime: String,
    entry: String,
    command: String,
    description: Option<String>,
}

#[derive(Debug, Clone, Serialize)]
#[serde(rename_all = "camelCase")]
struct ToolEvent {
    plugin_id: String,
    data: Value,
}

pub fn run_python_plugin(
    window: tauri::Window,
    payload: RunToolPayload,
) -> Result<RunToolResult, Box<dyn std::error::Error>> {
    // 插件目录：external-plugins/{pluginId}
    // 这里必须转成绝对路径，否则配合 current_dir 会导致路径重复拼接
    let raw_plugin_dir = get_plugin_dir(&payload.plugin_id);

    let plugin_dir = raw_plugin_dir.canonicalize().map_err(|error| {
        format!(
            "插件目录不存在或无法访问: {}\n{}",
            raw_plugin_dir.display(),
            error
        )
    })?;

    let manifest_path = plugin_dir.join("plugin.json");

    let manifest_text = fs::read_to_string(&manifest_path)?;
    let manifest: PluginManifest = serde_json::from_str(&manifest_text)?;

    validate_manifest(&payload, &manifest)?;

    let raw_entry_path = plugin_dir.join(&manifest.entry);

    if !raw_entry_path.exists() {
        return Err(format!("插件入口文件不存在: {}", raw_entry_path.display()).into());
    }

    // 入口文件也转绝对路径
    let entry_path = raw_entry_path.canonicalize()?;

    validate_plugin_input(&payload)?;

    let plugin_id = payload.plugin_id.clone();
    let input_text = serde_json::to_string(&payload.input)?;

    // 优先使用插件自己的 .venv
    let python_path = resolve_python_path(&plugin_dir);

    window.emit(
        "tool-log",
        json!({
            "pluginId": plugin_id,
            "data": {
                "message": format!("[PLUGIN] 使用 Python: {}", python_path.display())
            }
        }),
    )?;

    window.emit(
        "tool-log",
        json!({
            "pluginId": plugin_id,
            "data": {
                "message": format!("[PLUGIN] 插件目录: {}", plugin_dir.display())
            }
        }),
    )?;

    window.emit(
        "tool-log",
        json!({
            "pluginId": plugin_id,
            "data": {
                "message": format!("[PLUGIN] 入口文件: {}", entry_path.display())
            }
        }),
    )?;

    let mut child = Command::new(&python_path)
        .arg(&entry_path)
        .env("PYTHONIOENCODING", "utf-8")
        .env("PYTHONUTF8", "1")
        // 插件运行时的工作目录固定为插件目录
        .current_dir(&plugin_dir)
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .spawn()
        .map_err(|error| {
            format!(
                "启动 Python 插件失败: {}\npython: {}\nentry: {}\nplugin_dir: {}",
                error,
                python_path.display(),
                entry_path.display(),
                plugin_dir.display()
            )
        })?;

    {
        let stdin = child.stdin.as_mut().ok_or("无法打开 Python stdin")?;
        stdin.write_all(input_text.as_bytes())?;
    }

    drop(child.stdin.take());

    let stdout = child.stdout.take().ok_or("无法读取 Python stdout")?;
    let stderr = child.stderr.take().ok_or("无法读取 Python stderr")?;

    let stderr_handle = thread::spawn(move || {
        let mut reader = BufReader::new(stderr);
        let mut stderr_text = String::new();
        let _ = reader.read_to_string(&mut stderr_text);
        stderr_text
    });

    let reader = BufReader::new(stdout);
    let mut final_result: Option<RunToolResult> = None;

    for line in reader.lines() {
        let line = line?;
        let line = line.trim();

        if line.is_empty() {
            continue;
        }

        let value: Value = match serde_json::from_str(line) {
            Ok(value) => value,
            Err(_) => {
                // Python stdout 里如果有非 JSON 内容，先当日志抛给前端
                window.emit(
                    "tool-log",
                    json!({
                        "pluginId": plugin_id,
                        "data": {
                            "message": line
                        }
                    }),
                )?;

                continue;
            }
        };

        let message_type = value
            .get("type")
            .and_then(|value| value.as_str())
            .unwrap_or("");

        match message_type {
            "progress" => {
                let data = value.get("data").cloned().unwrap_or(Value::Null);

                window.emit(
                    "tool-progress",
                    ToolEvent {
                        plugin_id: plugin_id.clone(),
                        data,
                    },
                )?;
            }

            "log" => {
                let data = value.get("data").cloned().unwrap_or(Value::Null);

                window.emit(
                    "tool-log",
                    ToolEvent {
                        plugin_id: plugin_id.clone(),
                        data,
                    },
                )?;
            }

            "result" => {
                let result_value = value
                    .get("data")
                    .cloned()
                    .ok_or("result 类型输出缺少 data 字段")?;

                let result: RunToolResult = serde_json::from_value(result_value)?;
                final_result = Some(result);
            }

            _ => {
                // 兼容旧插件：直接输出 RunToolResult
                let result: RunToolResult = serde_json::from_value(value)?;
                final_result = Some(result);
            }
        }
    }

    let output_status = child.wait()?;

    let stderr_text = stderr_handle
        .join()
        .unwrap_or_else(|_| "读取 stderr 失败".to_string());

    if !output_status.success() {
        return Err(format!(
            "Python 插件执行失败\npython: {}\nentry: {}\nplugin_dir: {}\nstderr:\n{}",
            python_path.display(),
            entry_path.display(),
            plugin_dir.display(),
            stderr_text
        )
        .into());
    }

    final_result.ok_or_else(|| "Python 插件没有输出最终结果".into())
}

fn validate_manifest(
    payload: &RunToolPayload,
    manifest: &PluginManifest,
) -> Result<(), Box<dyn std::error::Error>> {
    if manifest.id != payload.plugin_id {
        return Err(format!(
            "插件 ID 不匹配，期望: {}，实际: {}",
            payload.plugin_id, manifest.id
        )
        .into());
    }

    if manifest.runtime != "python" {
        return Err(format!("暂不支持的插件运行时: {}", manifest.runtime).into());
    }

    Ok(())
}

fn get_plugin_dir(plugin_id: &str) -> PathBuf {
    PathBuf::from("../external-plugins").join(plugin_id)
}

fn get_app_root_dir() -> PathBuf {
    PathBuf::from("..")
}

fn resolve_python_path(plugin_dir: &Path) -> PathBuf {
    // 1. 优先使用插件自己的 venv
    // external-plugins/{pluginId}/.venv/Scripts/python.exe
    let plugin_venv_python = plugin_dir.join(".venv").join("Scripts").join("python.exe");

    if plugin_venv_python.exists() {
        return plugin_venv_python
            .canonicalize()
            .unwrap_or(plugin_venv_python);
    }

    // 2. 使用项目公共 venv
    // 项目根目录/.venv/Scripts/python.exe
    let app_venv_python = get_app_root_dir()
        .join(".venv")
        .join("Scripts")
        .join("python.exe");

    if app_venv_python.exists() {
        return app_venv_python.canonicalize().unwrap_or(app_venv_python);
    }

    // 3. 兜底使用系统 python
    PathBuf::from("python")
}

fn validate_plugin_input(payload: &RunToolPayload) -> Result<(), Box<dyn std::error::Error>> {
    match payload.plugin_id.as_str() {
        "folder-flatten" => validate_source_dir(payload),
        _ => Ok(()),
    }
}

fn validate_source_dir(payload: &RunToolPayload) -> Result<(), Box<dyn std::error::Error>> {
    let source_dir = payload
        .input
        .get("sourceDir")
        .and_then(|value| value.as_str())
        .ok_or("缺少 sourceDir 参数")?;

    let source_path = PathBuf::from(source_dir);

    if !source_path.exists() {
        return Err(format!("文件夹不存在: {}", source_dir).into());
    }

    if !source_path.is_dir() {
        return Err(format!("不是有效文件夹: {}", source_dir).into());
    }

    Ok(())
}

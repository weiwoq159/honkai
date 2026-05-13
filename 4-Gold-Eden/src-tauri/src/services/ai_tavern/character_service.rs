use crate::models::ai_tavern::TavernCharacterSummary;
use serde_json::Value;
use std::fs;
use std::path::{Path, PathBuf};
use tauri::{AppHandle, Manager};

pub fn list_tavern_characters(app: AppHandle) -> Result<Vec<TavernCharacterSummary>, String> {
    let characters_dir = get_builtin_characters_dir(&app)?;

    if !characters_dir.exists() {
        return Ok(vec![]);
    }

    let entries =
        fs::read_dir(&characters_dir).map_err(|error| format!("读取角色目录失败：{}", error))?;

    let mut list: Vec<TavernCharacterSummary> = Vec::new();

    for entry in entries {
        let entry = match entry {
            Ok(value) => value,
            Err(error) => {
                eprintln!("读取角色目录项失败：{}", error);
                continue;
            }
        };

        let character_dir = entry.path();

        if !character_dir.is_dir() {
            continue;
        }

        let character_json_path = character_dir.join("character.json");

        if !character_json_path.exists() {
            continue;
        }

        match read_character_summary(&character_dir, &character_json_path) {
            Ok(summary) => list.push(summary),
            Err(error) => {
                eprintln!(
                    "读取角色失败：{}，路径：{}",
                    error,
                    character_json_path.display()
                );
            }
        }
    }

    list.sort_by(|a, b| a.name.cmp(&b.name));

    Ok(list)
}

fn get_builtin_characters_dir(app: &AppHandle) -> Result<PathBuf, String> {
    // 1. 开发环境：读取 src-tauri/resources
    let dev_dir = PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .join("resources")
        .join("ai-tavern")
        .join("characters");

    if dev_dir.exists() {
        return Ok(dev_dir);
    }

    // 2. 生产环境：读取打包后的 resource_dir
    let resource_dir = app
        .path()
        .resource_dir()
        .map_err(|error| format!("获取 resource_dir 失败：{}", error))?;

    let prod_dir = resource_dir
        .join("resources")
        .join("ai-tavern")
        .join("characters");

    Ok(prod_dir)
}

fn read_character_summary(
    character_dir: &Path,
    character_json_path: &Path,
) -> Result<TavernCharacterSummary, String> {
    let content = fs::read_to_string(character_json_path)
        .map_err(|error| format!("读取 character.json 失败：{}", error))?;

    let json: Value = serde_json::from_str(&content)
        .map_err(|error| format!("解析 character.json 失败：{}", error))?;

    let folder_name = character_dir
        .file_name()
        .and_then(|value| value.to_str())
        .unwrap_or("")
        .to_string();

    let id = json
        .get("id")
        .and_then(|value| value.as_str())
        .map(|value| value.to_string())
        .filter(|value| !value.trim().is_empty())
        .unwrap_or_else(|| folder_name.clone());

    let name = json
        .get("name")
        .and_then(|value| value.as_str())
        .map(|value| value.to_string())
        .or_else(|| {
            json.pointer("/CHARACTER_MODELING/CORE_PROFILE/name")
                .and_then(|value| value.as_str())
                .map(|value| value.to_string())
        })
        .filter(|value| !value.trim().is_empty())
        .unwrap_or_else(|| folder_name.clone());

    let description = json
        .get("description")
        .and_then(|value| value.as_str())
        .map(|value| value.to_string())
        .or_else(|| {
            json.pointer("/CHARACTER_MODELING/CORE_PROFILE/background")
                .and_then(|value| value.as_str())
                .map(|value| value.to_string())
        });

    let avatar_file_name = json
        .get("avatar")
        .and_then(|value| value.as_str())
        .unwrap_or("avatar.png");

    let avatar_path = character_dir.join(avatar_file_name);

    let avatar_path = if avatar_path.exists() {
        Some(avatar_path.to_string_lossy().to_string())
    } else {
        None
    };

    let updated_at = fs::metadata(character_json_path)
        .ok()
        .and_then(|metadata| metadata.modified().ok())
        .and_then(|time| time.duration_since(std::time::UNIX_EPOCH).ok())
        .map(|duration| duration.as_millis() as i64);

    Ok(TavernCharacterSummary {
        id,
        name,
        avatar_path,
        character_path: character_json_path.to_string_lossy().to_string(),
        description,
        updated_at,
    })
}

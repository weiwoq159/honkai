import json
import sys
from pathlib import Path


DEFAULT_EXCLUDE_DIRS = {
    ".git",
    ".svn",
    ".hg",
    "node_modules",
    ".next",
    ".nuxt",
    "dist",
    "build",
    "target",
    "__pycache__",
    ".venv",
    "venv",
    ".idea",
}


def read_input():
    try:
        raw = sys.stdin.read().strip()

        if not raw:
            return {}

        return json.loads(raw)
    except Exception as error:
        raise ValueError(f"读取输入参数失败：{error}")


def normalize_payload(payload):
    """
    兼容几种可能的 Python stdin 入参结构：

    1. 直接收到 input：
       {
         "action": "run",
         "config": {
           "folderPath": "...",
           "maxDepth": 3
         }
       }

    2. 收到完整 payload：
       {
         "pluginId": "folder-tree",
         "input": {
           "action": "run",
           "config": {
             "folderPath": "...",
             "maxDepth": 3
           }
         }
       }

    3. 只收到 config：
       {
         "folderPath": "...",
         "maxDepth": 3
       }
    """
    if not isinstance(payload, dict):
        return {
            "action": "run",
            "config": {},
        }

    # 情况 2：Rust runner 把完整 payload 传给 Python
    if isinstance(payload.get("input"), dict):
        input_data = payload.get("input") or {}

        if isinstance(input_data.get("config"), dict):
            return {
                "action": input_data.get("action", "run"),
                "config": input_data.get("config") or {},
            }

        return {
            "action": input_data.get("action", "run"),
            "config": input_data,
        }

    # 情况 1：Rust runner 只把 input 传给 Python
    if isinstance(payload.get("config"), dict):
        return {
            "action": payload.get("action", "run"),
            "config": payload.get("config") or {},
        }

    # 情况 3：Rust runner 只把 config 传给 Python
    return {
        "action": payload.get("action", "run"),
        "config": payload,
    }


def to_bool(value, default=False):
    if isinstance(value, bool):
        return value

    if value is None:
        return default

    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "y", "on"}

    return bool(value)


def is_hidden_path(path: Path) -> bool:
    return path.name.startswith(".")


def should_skip(path: Path, include_hidden: bool) -> bool:
    if not include_hidden and is_hidden_path(path):
        return True

    if path.is_dir() and path.name in DEFAULT_EXCLUDE_DIRS:
        return True

    return False


def safe_iterdir(path: Path):
    try:
        return sorted(
            path.iterdir(),
            key=lambda item: (not item.is_dir(), item.name.lower()),
        )
    except PermissionError:
        return []
    except FileNotFoundError:
        return []
    except OSError:
        return []


def build_tree_lines(
    root: Path,
    max_depth: int,
    include_files: bool,
    include_hidden: bool,
):
    lines = []
    total_dirs = 0
    total_files = 0

    root_name = root.name or str(root)
    lines.append(f"{root_name}/")

    def walk(current_path: Path, prefix: str, depth: int):
        nonlocal total_dirs, total_files

        if depth > max_depth:
            return

        children = []

        for child in safe_iterdir(current_path):
            if should_skip(child, include_hidden):
                continue

            if child.is_dir():
                children.append(child)
            elif include_files and child.is_file():
                children.append(child)

        for index, child in enumerate(children):
            is_last = index == len(children) - 1
            connector = "└─ " if is_last else "├─ "
            next_prefix = prefix + ("   " if is_last else "│  ")

            if child.is_dir():
                total_dirs += 1
                lines.append(f"{prefix}{connector}{child.name}/")
                walk(child, next_prefix, depth + 1)
            else:
                total_files += 1
                lines.append(f"{prefix}{connector}{child.name}")

    walk(root, "", 1)

    return lines, total_dirs, total_files


def build_markdown(
    folder_path: str,
    max_depth: int,
    include_files: bool,
    include_hidden: bool,
):
    root = Path(folder_path).expanduser().resolve()

    if not root.exists():
        raise FileNotFoundError(f"目标文件夹不存在：{root}")

    if not root.is_dir():
        raise NotADirectoryError(f"目标路径不是文件夹：{root}")

    lines, total_dirs, total_files = build_tree_lines(
        root=root,
        max_depth=max_depth,
        include_files=include_files,
        include_hidden=include_hidden,
    )

    markdown = "```txt\n" + "\n".join(lines) + "\n```"

    return {
        "folderPath": str(root),
        "totalDirs": total_dirs,
        "totalFiles": total_files,
        "markdown": markdown,
    }


def success(message: str, data=None, logs=None):
    result = {
        "success": True,
        "message": message,
        "data": data or {},
        "logs": logs or [],
    }

    print(json.dumps(result, ensure_ascii=False), flush=True)


def fail(message: str, logs=None, debug=None):
    result = {
        "success": False,
        "message": message,
        "data": {
            "debug": debug or {},
        },
        "logs": logs or [],
    }

    print(json.dumps(result, ensure_ascii=False), flush=True)


def main():
    logs = []
    payload = None

    try:
        payload = read_input()
        normalized = normalize_payload(payload)

        action = normalized.get("action", "run")
        config = normalized.get("config", {})

        if action != "run":
            raise ValueError(f"不支持的 action：{action}")

        folder_path = str(config.get("folderPath", "")).strip()
        max_depth = int(config.get("maxDepth", 3))
        include_files = to_bool(config.get("includeFiles", True), True)
        include_hidden = to_bool(config.get("includeHidden", False), False)

        if not folder_path:
            raise ValueError("缺少参数：folderPath")

        if max_depth < 1:
            raise ValueError("maxDepth 不能小于 1")

        logs.append(f"[INFO] 开始生成目录结构：{folder_path}")
        logs.append(f"[INFO] 扫描深度：{max_depth}")
        logs.append(f"[INFO] 包含文件：{include_files}")
        logs.append(f"[INFO] 包含隐藏文件：{include_hidden}")

        data = build_markdown(
            folder_path=folder_path,
            max_depth=max_depth,
            include_files=include_files,
            include_hidden=include_hidden,
        )

        logs.append("[SUCCESS] 目录结构生成完成")
        logs.append(f"[INFO] 文件夹数量：{data.get('totalDirs', 0)}")
        logs.append(f"[INFO] 文件数量：{data.get('totalFiles', 0)}")

        success(
            message="目录结构获取完成",
            data=data,
            logs=logs,
        )

    except Exception as error:
        logs.append(f"[ERROR] {error}")

        debug = {
            "payloadKeys": list(payload.keys()) if isinstance(payload, dict) else [],
            "payload": payload,
        }

        fail(
            message=f"目录结构获取失败：{error}",
            logs=logs,
            debug=debug,
        )


if __name__ == "__main__":
    main()
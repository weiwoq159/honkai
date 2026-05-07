import json
import sys
from pathlib import Path


def build_tree(path: Path, root: Path, current_depth: int, max_depth: int, include_files: bool) -> dict:
    node = {
        "name": path.name,
        "path": str(path),
        "relativePath": str(path.relative_to(root)) if path != root else "",
        "type": "directory" if path.is_dir() else "file",
        "children": []
    }

    if path.is_file():
        try:
            node["size"] = path.stat().st_size
        except OSError:
            node["size"] = 0
        return node

    if current_depth >= max_depth:
        node["truncated"] = True
        return node

    try:
        children = sorted(
            path.iterdir(),
            key=lambda item: (item.is_file(), item.name.lower())
        )
    except PermissionError:
        node["error"] = "无权限访问"
        return node
    except OSError as error:
        node["error"] = str(error)
        return node

    for child in children:
        if child.is_file() and not include_files:
            continue

        node["children"].append(
            build_tree(
                path=child,
                root=root,
                current_depth=current_depth + 1,
                max_depth=max_depth,
                include_files=include_files
            )
        )

    return node


def count_nodes(node: dict) -> tuple[int, int]:
    folder_count = 1 if node.get("type") == "directory" else 0
    file_count = 1 if node.get("type") == "file" else 0

    for child in node.get("children", []):
        child_folder_count, child_file_count = count_nodes(child)
        folder_count += child_folder_count
        file_count += child_file_count

    return folder_count, file_count


def run(input_data: dict) -> dict:
    source_dir = input_data.get("sourceDir")
    max_depth = int(input_data.get("maxDepth", 5))
    include_files = bool(input_data.get("includeFiles", True))

    if not source_dir:
        return {
            "success": False,
            "message": "缺少 sourceDir 参数",
            "data": None
        }

    root = Path(source_dir).resolve()

    if not root.exists():
        return {
            "success": False,
            "message": f"路径不存在: {source_dir}",
            "data": None
        }

    if not root.is_dir():
        return {
            "success": False,
            "message": f"不是有效文件夹: {source_dir}",
            "data": None
        }

    tree = build_tree(
        path=root,
        root=root,
        current_depth=0,
        max_depth=max_depth,
        include_files=include_files
    )

    folder_count, file_count = count_nodes(tree)

    return {
        "success": True,
        "message": "目录结构获取成功",
        "data": {
            "sourceDir": str(root),
            "maxDepth": max_depth,
            "includeFiles": include_files,
            "folderCount": folder_count,
            "fileCount": file_count,
            "tree": tree
        }
    }


if __name__ == "__main__":
    try:
        raw_input = sys.stdin.read()
        input_data = json.loads(raw_input) if raw_input else {}

        result = run(input_data)

        print(json.dumps(result, ensure_ascii=True))

    except Exception as error:
        result = {
            "success": False,
            "message": str(error),
            "data": None
        }

        print(json.dumps(result, ensure_ascii=True))
        sys.exit(1)
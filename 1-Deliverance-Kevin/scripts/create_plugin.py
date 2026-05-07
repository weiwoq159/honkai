import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def to_pascal_case(text: str) -> str:
    return "".join(word.capitalize() for word in text.split("-"))


def to_camel_case(text: str) -> str:
    pascal = to_pascal_case(text)
    return pascal[0].lower() + pascal[1:]


def create_file(path: Path, content: str):
    if path.exists():
        print(f"[skip] 文件已存在: {path}")
        return

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print(f"[create] {path}")


def build_plugin_json(plugin_id: str, name: str, description: str) -> str:
    return f'''{{
  "id": "{plugin_id}",
  "name": "{name}",
  "version": "0.1.0",
  "runtime": "python",
  "entry": "main.py",
  "command": "run",
  "description": "{description}"
}}
'''


def build_main_py() -> str:
    return '''import json
import sys


def run(input_data: dict) -> dict:
    return {
        "success": True,
        "message": "插件执行成功",
        "data": input_data
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
'''


def build_plugin_ts(
    plugin_id: str,
    name: str,
    description: str,
    order: int,
    category: str,
) -> str:
    pascal = to_pascal_case(plugin_id)
    camel = to_camel_case(plugin_id)

    return f'''import {{ lazy }} from "react";
import type {{ ToolPlugin }} from "@plugins/types";

export const {camel}Plugin: ToolPlugin = {{
  id: "{plugin_id}",
  name: "{name}",
  description: "{description}",
  category: "{category}",
  path: "/tools/{plugin_id}",
  order: {order},
  page: lazy(() =>
    import("./pages/{pascal}Page").then((module) => ({{
      default: module.{pascal}Page,
    }})),
  ),
}};
'''


def build_types_ts(plugin_id: str) -> str:
    pascal = to_pascal_case(plugin_id)

    return f'''export interface {pascal}Input {{
  sourceDir: string;
}}

export interface {pascal}Data {{
  sourceDir?: string;
}}
'''


def build_page_tsx(plugin_id: str, name: str, description: str) -> str:
    pascal = to_pascal_case(plugin_id)

    return f'''import {{ Card, Typography }} from "antd";

const {{ Title, Paragraph }} = Typography;

export function {pascal}Page() {{
  return (
    <Card>
      <Title level={{3}} style={{{{ marginTop: 0 }}}}>
        {name}
      </Title>

      <Paragraph type="secondary">
        {description}
      </Paragraph>
    </Card>
  );
}}
'''


def register_plugin(plugin_id: str):
    registry_path = ROOT / "src" / "plugins" / "registry.ts"

    if not registry_path.exists():
        print(f"[warn] registry.ts 不存在，跳过自动注册: {registry_path}")
        return

    content = registry_path.read_text(encoding="utf-8")

    camel = to_camel_case(plugin_id)
    plugin_var = f"{camel}Plugin"
    import_line = f'import {{ {plugin_var} }} from "@features/{plugin_id}/plugin";'

    if import_line not in content:
        lines = content.splitlines()

        last_import_index = -1
        for index, line in enumerate(lines):
            if line.startswith("import "):
                last_import_index = index

        if last_import_index >= 0:
            lines.insert(last_import_index + 1, import_line)
        else:
            lines.insert(0, import_line)

        content = "\n".join(lines) + "\n"
        print(f"[update] 已添加 import: {import_line}")
    else:
        print(f"[skip] import 已存在: {import_line}")

    if plugin_var in content.split("export const plugins", 1)[-1]:
        print(f"[skip] 插件已在 plugins 数组中: {plugin_var}")
        registry_path.write_text(content, encoding="utf-8")
        return

    marker = "export const plugins: ToolPlugin[] = ["

    if marker not in content:
        print("[warn] 没找到 plugins 数组，跳过自动插入")
        registry_path.write_text(content, encoding="utf-8")
        return

    content = content.replace(
        marker,
        f"{marker}\n  {plugin_var},",
        1,
    )

    registry_path.write_text(content, encoding="utf-8")
    print(f"[update] 已注册插件: {plugin_var}")


def parse_order() -> int:
    if len(sys.argv) < 5:
        return 999

    raw_order = sys.argv[4]

    try:
        return int(raw_order)
    except ValueError:
        print(f"[warn] order 必须是数字，当前收到: {raw_order}，已使用默认值 999")
        return 999


def parse_category() -> str:
    if len(sys.argv) < 6:
        return "文件处理"

    raw_category = sys.argv[5].strip()

    if not raw_category:
        return "文件处理"

    return raw_category


def main():
    if len(sys.argv) < 2:
        print("用法: python scripts/create_plugin.py <plugin-id> [name] [description] [order] [category]")
        print('示例: python scripts/create_plugin.py empty-folder-cleaner "空文件夹清理" "扫描并清理指定目录下的空文件夹" 40 "文件处理"')
        print('示例: python scripts/create_plugin.py pica-comic-crawler "哔咔漫画爬取" "根据章节分页接口下载漫画图片" 80 "爬虫"')
        sys.exit(1)

    plugin_id = sys.argv[1]
    name = sys.argv[2] if len(sys.argv) >= 3 else plugin_id
    description = sys.argv[3] if len(sys.argv) >= 4 else name
    order = parse_order()
    category = parse_category()

    pascal = to_pascal_case(plugin_id)

    external_dir = ROOT / "external-plugins" / plugin_id
    feature_dir = ROOT / "src" / "features" / plugin_id

    create_file(
        external_dir / "plugin.json",
        build_plugin_json(plugin_id, name, description),
    )

    create_file(
        external_dir / "main.py",
        build_main_py(),
    )

    create_file(
        feature_dir / "plugin.ts",
        build_plugin_ts(plugin_id, name, description, order, category),
    )

    create_file(
        feature_dir / "types.ts",
        build_types_ts(plugin_id),
    )

    create_file(
        feature_dir / "pages" / f"{pascal}Page.tsx",
        build_page_tsx(plugin_id, name, description),
    )

    print("")
    print("生成完成。")
    print("")
    print("已尝试自动注册到 src/plugins/registry.ts：")
    register_plugin(plugin_id)
    print("")
    print("如果自动注册失败，请手动添加：")
    print("")
    print(f'import {{ {to_camel_case(plugin_id)}Plugin }} from "@features/{plugin_id}/plugin";')
    print("")
    print("然后加入 plugins 数组：")
    print("")
    print(f"{to_camel_case(plugin_id)}Plugin,")
    print("")
    print("插件排序 order：")
    print("")
    print(order)
    print("")
    print("插件分类 category：")
    print("")
    print(category)


if __name__ == "__main__":
    main()
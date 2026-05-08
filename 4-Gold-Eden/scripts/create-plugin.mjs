import fs from "node:fs";
import path from "node:path";

const ROOT_DIR = process.cwd();

const VALID_CATEGORIES = ["collector", "automation", "file-tools"];

const CATEGORY_EXPORT_NAME_MAP = {
  collector: "collectorPlugins",
  automation: "automationPlugins",
  "file-tools": "fileToolPlugins",
};

function parseArgs() {
  const args = process.argv.slice(2);
  const result = {};

  for (let index = 0; index < args.length; index += 1) {
    const item = args[index];

    if (!item.startsWith("--")) {
      continue;
    }

    const key = item.replace(/^--/, "");
    const value = args[index + 1];

    if (!value || value.startsWith("--")) {
      result[key] = true;
    } else {
      result[key] = value;
      index += 1;
    }
  }

  return result;
}

function ensureDir(dirPath) {
  fs.mkdirSync(dirPath, { recursive: true });
}

function writeFileSafe(filePath, content) {
  if (fs.existsSync(filePath)) {
    console.log(`[SKIP] 已存在：${filePath}`);
    return;
  }

  ensureDir(path.dirname(filePath));
  fs.writeFileSync(filePath, content, "utf-8");
  console.log(`[CREATE] ${filePath}`);
}

function toPascalCase(text) {
  return text
    .split(/[-_\s]+/)
    .filter(Boolean)
    .map((item) => item.charAt(0).toUpperCase() + item.slice(1))
    .join("");
}

function createExternalPlugin({ category, pluginId, name, description }) {
  const pluginRoot = path.join(
    ROOT_DIR,
    "external-plugins",
    category,
    pluginId,
  );

  writeFileSafe(
    path.join(pluginRoot, "plugin.json"),
    `${JSON.stringify(
      {
        id: pluginId,
        name,
        version: "0.1.0",
        runtime: "python",
        entry: "main.py",
        category,
        description,
      },
      null,
      2,
    )}\n`,
  );

  writeFileSafe(
    path.join(pluginRoot, "main.py"),
    `import json
import sys


def main():
    result = {
        "success": True,
        "message": "${name} 执行完成",
        "data": {
            "pluginId": "${pluginId}",
            "name": "${name}"
        },
        "logs": [
            "[INFO] ${name} 开始执行",
            "[SUCCESS] ${name} 执行完成"
        ]
    }

    print(json.dumps(result, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
`,
  );
}

function createFrontendPage({ category, pluginId, name }) {
  const componentName = `${toPascalCase(pluginId)}Page`;
  const categoryDir = path.join(ROOT_DIR, "src", "plugins", category);
  const pageFilePath = path.join(categoryDir, `${componentName}.tsx`);

  writeFileSafe(
    pageFilePath,
    `export function ${componentName}() {
  return <div>${name}</div>;
}
`,
  );

  return componentName;
}

function createOrUpdateCategoryRegistry({
  category,
  pluginId,
  name,
  description,
  componentName,
}) {
  const categoryDir = path.join(ROOT_DIR, "src", "plugins", category);
  const registryPath = path.join(categoryDir, "registry.ts");
  const exportName = CATEGORY_EXPORT_NAME_MAP[category];

  if (!exportName) {
    throw new Error(`未配置 category 对应的导出名：${category}`);
  }

  const importLine = `import { ${componentName} } from "./${componentName}";`;

  const pluginObject = `  {
    id: "${pluginId}",
    name: "${name}",
    description: "${description}",
    category: "${category}",
    path: "/plugins/${category}/${pluginId}",
    order: 100,
    component: ${componentName},
  },`;

  if (!fs.existsSync(registryPath)) {
    writeFileSafe(
      registryPath,
      `import type { FrontendPlugin } from "../types";
${importLine}

export const ${exportName}: FrontendPlugin[] = [
${pluginObject}
];
`,
    );

    return;
  }

  let content = fs.readFileSync(registryPath, "utf-8");

  if (content.includes(`id: "${pluginId}"`)) {
    console.log(`[SKIP] registry 已存在插件：${pluginId}`);
    return;
  }

  if (!content.includes(importLine)) {
    const exportIndex = content.indexOf("export const");

    if (exportIndex === -1) {
      throw new Error(`registry.ts 中没有找到 export const：${registryPath}`);
    }

    content =
      content.slice(0, exportIndex).trimEnd() +
      `\n${importLine}\n\n` +
      content.slice(exportIndex);
  }

  const registryPattern = new RegExp(
    `(export const ${exportName}: FrontendPlugin\\[\\] = \\[)([\\s\\S]*?)(\\];)`,
  );

  if (!registryPattern.test(content)) {
    throw new Error(`无法定位 ${exportName} 数组：${registryPath}`);
  }

  content = content.replace(registryPattern, (_match, start, body, end) => {
    return `${start}${body.trimEnd()}\n${pluginObject}\n${end}`;
  });

  fs.writeFileSync(registryPath, content, "utf-8");
  console.log(`[UPDATE] ${registryPath}`);
}

function main() {
  const args = parseArgs();

  const category = String(args.category || "").trim();
  const pluginId = String(args.id || "").trim();
  const name = String(args.name || "").trim();
  const description = String(args.description || "").trim();

  if (!category) {
    throw new Error("缺少参数：--category");
  }

  if (!VALID_CATEGORIES.includes(category)) {
    throw new Error(
      `不支持的 category：${category}，只支持：${VALID_CATEGORIES.join(", ")}`,
    );
  }

  if (!pluginId) {
    throw new Error("缺少参数：--id");
  }

  if (!/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(pluginId)) {
    throw new Error(
      "插件 id 只能使用小写英文、数字和短横线，例如：pica-comic-crawler",
    );
  }

  if (!name) {
    throw new Error("缺少参数：--name");
  }

  if (!description) {
    throw new Error("缺少参数：--description");
  }

  createExternalPlugin({
    category,
    pluginId,
    name,
    description,
  });

  const componentName = createFrontendPage({
    category,
    pluginId,
    name,
  });

  createOrUpdateCategoryRegistry({
    category,
    pluginId,
    name,
    description,
    componentName,
  });

  console.log("");
  console.log("插件基础模板创建完成");
}

main();

import fs from "node:fs";
import path from "node:path";
import crypto from "node:crypto";

const ROOT_DIR = process.cwd();

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

function readJson(filePath) {
  if (!fs.existsSync(filePath)) {
    throw new Error(`模板文件不存在：${filePath}`);
  }

  const content = fs.readFileSync(filePath, "utf-8");
  return JSON.parse(content);
}

function writeJsonSafe(filePath, data) {
  if (fs.existsSync(filePath)) {
    console.log(`[SKIP] 已存在：${filePath}`);
    return false;
  }

  ensureDir(path.dirname(filePath));
  fs.writeFileSync(filePath, `${JSON.stringify(data, null, 2)}\n`, "utf-8");
  console.log(`[CREATE] ${filePath}`);
  return true;
}

function writeFileSafe(filePath, content) {
  if (fs.existsSync(filePath)) {
    console.log(`[SKIP] 已存在：${filePath}`);
    return false;
  }

  ensureDir(path.dirname(filePath));
  fs.writeFileSync(filePath, content, "utf-8");
  console.log(`[CREATE] ${filePath}`);
  return true;
}

function createLocalId() {
  const timestamp = Date.now().toString(36);
  const randomPart = crypto.randomBytes(8).toString("hex");

  return `char_${timestamp}_${randomPart}`;
}

function setByPath(target, pathText, value) {
  const keys = pathText.split(".");
  let current = target;

  for (let index = 0; index < keys.length - 1; index += 1) {
    const key = keys[index];

    if (
      current[key] === undefined ||
      current[key] === null ||
      typeof current[key] !== "object" ||
      Array.isArray(current[key])
    ) {
      current[key] = {};
    }

    current = current[key];
  }

  current[keys[keys.length - 1]] = value;
}

function patchCharacterTemplate(template, { localId, name }) {
  const timestamp = Date.now();

  /**
   * Node 17+ 支持 structuredClone。
   * 如果你 Node 版本太低，可以换成 JSON.parse(JSON.stringify(template))。
   */
  const character =
    typeof structuredClone === "function"
      ? structuredClone(template)
      : JSON.parse(JSON.stringify(template));

  /**
   * 外层系统字段：
   * 给 Rust / SQLite / 前端列表 / 资源路径管理使用。
   */
  character.localId = localId;
  character.id = localId;
  character.sourceId = character.sourceId || "";
  character.sourceType = character.sourceType || "manual";
  character.name = name;
  character.avatar = character.avatar || "avatar.png";
  character.fullbody = character.fullbody || "fullbody.png";
  character.createdAt = timestamp;
  character.updatedAt = timestamp;

  /**
   * 同步写入角色卡主体字段：
   * 给 prompt、角色编辑器、详情页使用。
   */
  setByPath(character, "CHARACTER_MODELING.CORE_PROFILE.name", name);
  setByPath(character, "CHARACTER_MODELING.CORE_PROFILE.real_name", name);

  return character;
}

function main() {
  const args = parseArgs();
  const name = String(args.name || "").trim();

  if (!name) {
    throw new Error(
      '缺少参数：--name，例如：node scripts/create-tavern-character.mjs --name "萧若雪"',
    );
  }

  const localId = createLocalId();

  const templatePath = path.join(
    ROOT_DIR,
    "src-tauri",
    "resources",
    "ai-tavern",
    "templates",
    "demo.json",
  );

  const characterDir = path.join(
    ROOT_DIR,
    "src-tauri",
    "resources",
    "ai-tavern",
    "characters",
    localId,
  );

  const characterPath = path.join(characterDir, "character.json");
  const readmePath = path.join(characterDir, "README.md");

  const template = readJson(templatePath);

  const character = patchCharacterTemplate(template, {
    localId,
    name,
  });

  ensureDir(characterDir);

  writeJsonSafe(characterPath, character);

  writeFileSafe(
    readmePath,
    `# ${name}

## 角色信息

- 展示名：${name}
- 本地 ID：${localId}

## 目录说明

\`\`\`txt
${localId}/
├─ character.json   # 角色卡 JSON
├─ avatar.png       # 角色头像，需要手动放入
└─ fullbody.png     # 角色全身图，需要手动放入
\`\`\`

## 规则

- 文件夹名使用 localId，不使用角色名
- 角色名可以重复，也可以后续修改
- localId 不建议修改，它用于数据库、会话和资源关联
- 头像文件命名为 avatar.png
- 全身图文件命名为 fullbody.png
- character.json 内只保存相对资源名，不保存绝对路径
`,
  );

  console.log("");
  console.log("AI 酒馆角色目录创建完成");
  console.log("");
  console.log("角色信息：");
  console.log(`- name: ${name}`);
  console.log(`- localId: ${localId}`);
  console.log("");
  console.log("生成结果：");
  console.log(`- ${characterPath}`);
  console.log(`- ${readmePath}`);
  console.log("");
  console.log("接下来你可以手动放入：");
  console.log(`- ${path.join(characterDir, "avatar.png")}`);
  console.log(`- ${path.join(characterDir, "fullbody.png")}`);
}

main();

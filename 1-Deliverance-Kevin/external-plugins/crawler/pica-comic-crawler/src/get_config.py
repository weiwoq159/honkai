import json
from functools import lru_cache
from pathlib import Path
from typing import Any


ROOT_DIR = Path(__file__).resolve().parents[1]
CONFIG_FILE = ROOT_DIR / "config" / "config.json"

@lru_cache(maxsize=1)
def load_config() -> dict[str, Any]:
    if not CONFIG_FILE.exists():
        raise FileNotFoundError(f"配置文件不存在：{CONFIG_FILE}")

    with CONFIG_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def get_config_value(key: str, default: Any = None) -> Any:
    config = load_config()
    return config.get(key, default)


def get_required_config_value(key: str) -> Any:
    config = load_config()
    value = config.get(key)

    if value is None or value == "":
        raise ValueError(f"config.json 缺少配置项：{key}")

    return value


def build_api_url(path: str) -> str:
    global_url = get_required_config_value("global_url")

    return global_url.rstrip("/") + "/" + path.lstrip("/")
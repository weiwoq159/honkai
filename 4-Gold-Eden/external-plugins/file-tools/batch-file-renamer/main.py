from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


PLUGIN_DIR = Path(__file__).resolve().parent
SRC_DIR = PLUGIN_DIR / "src"
RENAMER_FILE = SRC_DIR / "renamer.py"

PROJECT_DIR = PLUGIN_DIR.parents[2]
SDK_DIR = PROJECT_DIR / "py-runtime" / "sdk"

for item in [PLUGIN_DIR, SRC_DIR, SDK_DIR]:
    item_str = str(item)
    if item_str not in sys.path:
        sys.path.insert(0, item_str)


from gold_eden_plugin.logger import get_logger
from gold_eden_plugin.result import success, fail
from gold_eden_plugin.runner import run_plugin


PLUGIN_ID = "batch-file-renamer"
logger = get_logger(PLUGIN_ID)


def load_batch_file_renamer_class():
    if not RENAMER_FILE.exists():
        raise FileNotFoundError(f"renamer.py 不存在：{RENAMER_FILE}")

    spec = importlib.util.spec_from_file_location(
        "batch_file_renamer_renamer",
        RENAMER_FILE,
    )

    if spec is None or spec.loader is None:
        raise ImportError(f"无法加载 renamer.py：{RENAMER_FILE}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    return module.BatchFileRenamer


def get_config(input_data: dict[str, Any]) -> dict[str, Any]:
    config = input_data.get("config")

    if isinstance(config, dict):
        return config

    return input_data


def handle(input_data: dict[str, Any]):
    try:
        config = get_config(input_data)

        BatchFileRenamer = load_batch_file_renamer_class()

        renamer = BatchFileRenamer(config)
        result = renamer.run()

        return success(
            message="批量重命名执行完成",
            data=result,
        )

    except Exception as error:
        logger.exception(f"批量重命名执行失败：{error}")

        return fail(
            message=str(error),
            data={
                "pluginId": PLUGIN_ID,
                "errorType": error.__class__.__name__,
            },
        )


if __name__ == "__main__":
    run_plugin(PLUGIN_ID, handle)
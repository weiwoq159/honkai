from pathlib import Path

try:
    from opencc import OpenCC
except ImportError:
    OpenCC = None


INVALID_FILENAME_CHARS = ['\\', '/', ':', '*', '?', '"', '<', '>', '|']


def to_simplified_text(text: str) -> str:
    if not text:
        return ""

    if OpenCC is None:
        return text

    cc = OpenCC("t2s")
    return cc.convert(text)


def safe_filename(name: str, fallback: str = "未命名") -> str:
    if not name:
        return fallback

    value = to_simplified_text(name).strip()

    for char in INVALID_FILENAME_CHARS:
        value = value.replace(char, "_")

    value = value.strip().rstrip(".")
    value = value[:120].strip()

    return value or fallback


def create_named_dir(base_dir: str | Path, name: str) -> Path:
    folder_name = safe_filename(name, fallback="未命名漫画")
    target_dir = Path(base_dir) / folder_name
    target_dir.mkdir(parents=True, exist_ok=True)
    return target_dir
from pathlib import Path
import requests


def download_images(images: list[dict], output_dir: str) -> list[str]:
    logs = []

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    for index, image in enumerate(images, start=1):
        url = image.get("url")
        filename = image.get("filename") or f"{index:03d}.jpg"

        if not url:
            logs.append(f"跳过第 {index} 张图片：缺少 url")
            continue

        file_path = output_path / filename

        response = requests.get(url, timeout=60)
        response.raise_for_status()

        file_path.write_bytes(response.content)

        logs.append(f"下载完成：{file_path}")

    return logs

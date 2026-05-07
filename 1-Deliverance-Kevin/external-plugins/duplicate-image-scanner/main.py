import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, List, Set

from PIL import Image
import imagehash


IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
    ".bmp",
    ".gif",
    ".tif",
    ".tiff",
    ".ico",
}


def json_default(value):
    try:
        import numpy as np

        if isinstance(value, np.integer):
            return int(value)

        if isinstance(value, np.floating):
            return float(value)

        if isinstance(value, np.ndarray):
            return value.tolist()

    except ImportError:
        pass

    raise TypeError(f"Object of type {type(value).__name__} is not JSON serializable")


def emit_event(event: Dict[str, Any]):
    print(json.dumps(event, ensure_ascii=False, default=json_default), flush=True)


def emit_progress(stage: str, current: int, total: int, message: str):
    percent = 0

    if total > 0:
        percent = round(current / total * 100, 2)

    emit_event(
        {
            "type": "progress",
            "data": {
                "stage": stage,
                "current": current,
                "total": total,
                "percent": percent,
                "message": message,
            },
        }
    )


def emit_log(message: str, extra: Dict[str, Any] | None = None):
    data: Dict[str, Any] = {
        "message": message,
    }

    if extra:
        data.update(extra)

    emit_event(
        {
            "type": "log",
            "data": data,
        }
    )


def emit_result(success: bool, message: str, data: Dict[str, Any] | None = None):
    emit_event(
        {
            "type": "result",
            "data": {
                "success": success,
                "message": message,
                "data": data,
            },
        }
    )


def emit_final(message: str, data: Dict[str, Any]):
    emit_result(
        success=True,
        message=message,
        data=data,
    )


def emit_error(error: Exception):
    emit_result(
        success=False,
        message=str(error),
        data=None,
    )


def format_time(timestamp: float) -> str:
    return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")


def is_image_file(file_path: Path) -> bool:
    return file_path.suffix.lower() in IMAGE_EXTENSIONS


def collect_files(
    source_path: Path,
    recursive: bool,
    max_files: int,
) -> List[Path]:
    files: List[Path] = []
    iterator = source_path.rglob("*") if recursive else source_path.iterdir()

    emit_progress(
        stage="collecting",
        current=0,
        total=max_files,
        message=f"开始收集文件，最多扫描 {max_files} 个文件",
    )

    for path in iterator:
        if not path.is_file():
            continue

        files.append(path)

        if len(files) % 500 == 0:
            emit_progress(
                stage="collecting",
                current=len(files),
                total=max_files,
                message=f"正在收集文件：{len(files)}/{max_files}",
            )

        if len(files) >= max_files:
            break

    emit_progress(
        stage="collecting",
        current=len(files),
        total=max_files,
        message=f"文件收集完成，共收集 {len(files)} 个文件",
    )

    return sorted(files, key=lambda path: str(path).lower())


def calculate_quality_score(width: int, height: int, size: int) -> float:
    megapixels = width * height
    size_mb = size / 1024 / 1024

    return megapixels + size_mb * 1000


def scan_image_hashes(
    source_path: Path,
    recursive: bool,
    max_files: int,
    max_images: int,
) -> Dict[str, Any]:
    files = collect_files(
        source_path=source_path,
        recursive=recursive,
        max_files=max_files,
    )

    total_file_count = len(files)
    image_items: List[Dict[str, Any]] = []
    failed_items: List[Dict[str, str]] = []
    skipped_file_count = 0

    emit_progress(
        stage="hashing",
        current=0,
        total=total_file_count,
        message=f"开始计算图片哈希，最多处理 {max_images} 张图片",
    )

    for index, file_path in enumerate(files, start=1):
        if len(image_items) >= max_images:
            skipped_file_count = total_file_count - index + 1
            break

        if index % 10 == 0 or index == total_file_count:
            emit_progress(
                stage="hashing",
                current=index,
                total=total_file_count,
                message=f"正在计算图片哈希：{index}/{total_file_count}，已识别图片 {len(image_items)}/{max_images}",
            )

        if not is_image_file(file_path):
            continue

        try:
            stat = file_path.stat()

            with Image.open(file_path) as image:
                image_format = image.format or file_path.suffix.lower().lstrip(".")
                width, height = image.size
                hash_value = imagehash.phash(image.convert("RGB"))

            size = stat.st_size
            quality_score = calculate_quality_score(
                width=width,
                height=height,
                size=size,
            )

            image_items.append(
                {
                    "path": str(file_path),
                    "name": file_path.name,
                    "size": size,
                    "width": width,
                    "height": height,
                    "format": image_format,
                    "hashObject": hash_value,
                    "hash": str(hash_value),
                    "qualityScore": quality_score,
                    "modifiedAt": format_time(stat.st_mtime),
                }
            )

        except Exception as error:
            failed_items.append(
                {
                    "path": str(file_path),
                    "reason": str(error),
                }
            )

    emit_progress(
        stage="hashing",
        current=total_file_count,
        total=total_file_count,
        message=f"图片哈希计算完成，共识别图片 {len(image_items)} 张",
    )

    return {
        "totalFileCount": total_file_count,
        "imageItems": image_items,
        "failedItems": failed_items,
        "skippedFileCount": skipped_file_count,
        "maxFiles": max_files,
        "maxImages": max_images,
    }


class UnionFind:
    def __init__(self, size: int):
        self.parent = list(range(size))

    def find(self, index: int) -> int:
        if self.parent[index] != index:
            self.parent[index] = self.find(self.parent[index])

        return self.parent[index]

    def union(self, a: int, b: int):
        root_a = self.find(a)
        root_b = self.find(b)

        if root_a != root_b:
            self.parent[root_b] = root_a


def get_hash_bucket_key(hash_text: str, prefix_length: int = 4) -> str:
    return hash_text[:prefix_length]


def build_hash_buckets(
    image_items: List[Dict[str, Any]],
    prefix_length: int = 4,
) -> Dict[str, List[int]]:
    buckets: Dict[str, List[int]] = {}

    for index, item in enumerate(image_items):
        hash_text = item["hash"]
        bucket_key = get_hash_bucket_key(hash_text, prefix_length)

        if bucket_key not in buckets:
            buckets[bucket_key] = []

        buckets[bucket_key].append(index)

    return buckets


def build_duplicate_groups(
    image_items: List[Dict[str, Any]],
    threshold: int,
    limit: int,
    bucket_prefix_length: int = 4,
    max_bucket_size: int = 300,
) -> Dict[str, Any]:
    image_count = len(image_items)

    emit_progress(
        stage="bucketing",
        current=0,
        total=image_count,
        message=f"开始按 pHash 分桶，共 {image_count} 张图片",
    )

    if image_count <= 1:
        emit_progress(
            stage="done",
            current=100,
            total=100,
            message="图片数量不足，无需分组",
        )

        return {
            "groups": [],
            "comparedPairCount": 0,
            "skippedBucketCount": 0,
            "bucketCount": 0,
        }

    buckets = build_hash_buckets(
        image_items=image_items,
        prefix_length=bucket_prefix_length,
    )

    bucket_items = list(buckets.items())

    emit_progress(
        stage="bucketing",
        current=len(bucket_items),
        total=len(bucket_items),
        message=f"分桶完成，共 {len(bucket_items)} 个桶",
    )

    union_find = UnionFind(image_count)
    pair_distances: Dict[str, int] = {}

    compared_pair_count = 0
    skipped_bucket_count = 0

    emit_progress(
        stage="comparing",
        current=0,
        total=len(bucket_items),
        message="开始在桶内比较图片相似度",
    )

    for bucket_index, (_, indexes) in enumerate(bucket_items, start=1):
        if bucket_index % 10 == 0 or bucket_index == len(bucket_items):
            emit_progress(
                stage="comparing",
                current=bucket_index,
                total=len(bucket_items),
                message=f"正在比较桶内图片：{bucket_index}/{len(bucket_items)}",
            )

        if len(indexes) <= 1:
            continue

        if len(indexes) > max_bucket_size:
            skipped_bucket_count += 1
            indexes = indexes[:max_bucket_size]

        for i_pos in range(len(indexes)):
            i = indexes[i_pos]
            hash_i = image_items[i]["hashObject"]

            for j_pos in range(i_pos + 1, len(indexes)):
                j = indexes[j_pos]
                hash_j = image_items[j]["hashObject"]

                distance = int(hash_i - hash_j)
                compared_pair_count += 1

                if distance <= threshold:
                    union_find.union(i, j)

                    left = min(i, j)
                    right = max(i, j)
                    pair_distances[f"{left}:{right}"] = distance

    group_index_map: Dict[int, List[int]] = {}

    for index in range(image_count):
        root = union_find.find(index)

        if root not in group_index_map:
            group_index_map[root] = []

        group_index_map[root].append(index)

    emit_progress(
        stage="grouping",
        current=0,
        total=len(group_index_map),
        message="正在生成重复图片分组",
    )

    duplicate_groups: List[Dict[str, Any]] = []
    group_id = 1

    group_values = list(group_index_map.values())

    for group_index, indexes in enumerate(group_values, start=1):
        if group_index % 10 == 0 or group_index == len(group_values):
            emit_progress(
                stage="grouping",
                current=group_index,
                total=len(group_values),
                message=f"正在生成重复图片分组：{group_index}/{len(group_values)}",
            )

        if len(indexes) <= 1:
            continue

        files = []

        for index in indexes:
            item = image_items[index]
            min_distance = 0

            for other_index in indexes:
                if index == other_index:
                    continue

                left = min(index, other_index)
                right = max(index, other_index)
                key = f"{left}:{right}"

                if key in pair_distances:
                    distance = pair_distances[key]

                    if min_distance == 0 or distance < min_distance:
                        min_distance = distance

            files.append(
                {
                    "path": item["path"],
                    "name": item["name"],
                    "size": item["size"],
                    "width": item["width"],
                    "height": item["height"],
                    "format": item["format"],
                    "hash": item["hash"],
                    "distance": int(min_distance),
                    "qualityScore": item["qualityScore"],
                    "recommendedKeep": False,
                    "recommendedDelete": False,
                    "modifiedAt": item["modifiedAt"],
                }
            )

        files.sort(
            key=lambda item: (
                item["qualityScore"],
                item["width"] * item["height"],
                item["size"],
            ),
            reverse=True,
        )

        for file_index, file_item in enumerate(files):
            if file_index == 0:
                file_item["recommendedKeep"] = True
                file_item["recommendedDelete"] = False
            else:
                file_item["recommendedKeep"] = False
                file_item["recommendedDelete"] = True

        distances: List[int] = []

        for i in range(len(indexes)):
            for j in range(i + 1, len(indexes)):
                left = min(indexes[i], indexes[j])
                right = max(indexes[i], indexes[j])
                key = f"{left}:{right}"

                if key in pair_distances:
                    distances.append(pair_distances[key])

        duplicate_groups.append(
            {
                "groupId": group_id,
                "count": len(files),
                "minDistance": int(min(distances)) if distances else 0,
                "maxDistance": int(max(distances)) if distances else 0,
                "files": files,
            }
        )

        group_id += 1

    duplicate_groups.sort(
        key=lambda group: (
            group["count"],
            sum(file["size"] for file in group["files"]),
        ),
        reverse=True,
    )

    emit_progress(
        stage="done",
        current=100,
        total=100,
        message=f"重复图片分组完成，实际比较 {compared_pair_count} 对，跳过超大桶 {skipped_bucket_count} 个",
    )

    return {
        "groups": duplicate_groups[:limit],
        "comparedPairCount": compared_pair_count,
        "skippedBucketCount": skipped_bucket_count,
        "bucketCount": len(bucket_items),
    }


def scan_duplicate_images(
    source_dir: str,
    recursive: bool = True,
    threshold: int = 5,
    limit: int = 100,
    max_files: int = 5000,
    max_images: int = 1000,
    bucket_prefix_length: int = 4,
    max_bucket_size: int = 300,
) -> Dict[str, Any]:
    source_path = Path(source_dir).resolve()

    if not source_path.exists():
        raise FileNotFoundError(f"目录不存在: {source_dir}")

    if not source_path.is_dir():
        raise NotADirectoryError(f"不是有效文件夹: {source_dir}")

    if threshold < 0:
        raise ValueError("threshold 必须大于等于 0")

    if limit <= 0:
        raise ValueError("limit 必须大于 0")

    if max_files <= 0:
        raise ValueError("maxFiles 必须大于 0")

    if max_images <= 0:
        raise ValueError("maxImages 必须大于 0")

    if bucket_prefix_length <= 0:
        raise ValueError("bucketPrefixLength 必须大于 0")

    if max_bucket_size <= 0:
        raise ValueError("maxBucketSize 必须大于 0")

    scan_result = scan_image_hashes(
        source_path=source_path,
        recursive=recursive,
        max_files=max_files,
        max_images=max_images,
    )

    image_items = scan_result["imageItems"]
    failed_items = scan_result["failedItems"]

    group_result = build_duplicate_groups(
        image_items=image_items,
        threshold=threshold,
        limit=limit,
        bucket_prefix_length=bucket_prefix_length,
        max_bucket_size=max_bucket_size,
    )

    groups = group_result["groups"]

    duplicate_image_paths: Set[str] = set()

    for group in groups:
        for file_item in group["files"]:
            duplicate_image_paths.add(file_item["path"])

    return {
        "sourceDir": str(source_path),
        "recursive": recursive,
        "threshold": threshold,
        "totalFileCount": scan_result["totalFileCount"],
        "imageCount": len(image_items),
        "duplicateGroupCount": len(groups),
        "duplicateImageCount": len(duplicate_image_paths),
        "failedCount": len(failed_items),
        "skippedFileCount": scan_result["skippedFileCount"],
        "maxFiles": max_files,
        "maxImages": max_images,
        "bucketPrefixLength": bucket_prefix_length,
        "maxBucketSize": max_bucket_size,
        "bucketCount": group_result["bucketCount"],
        "comparedPairCount": group_result["comparedPairCount"],
        "skippedBucketCount": group_result["skippedBucketCount"],
        "limit": limit,
        "groups": groups,
        "failedItems": failed_items,
    }


def run(input_data: dict) -> Dict[str, Any]:
    source_dir = input_data.get("sourceDir")
    recursive = input_data.get("recursive", True)
    threshold = input_data.get("threshold", 5)
    limit = input_data.get("limit", 100)

    max_files = input_data.get("maxFiles", 5000)
    max_images = input_data.get("maxImages", 1000)
    bucket_prefix_length = input_data.get("bucketPrefixLength", 4)
    max_bucket_size = input_data.get("maxBucketSize", 300)

    if not source_dir:
        raise ValueError("sourceDir 不能为空")

    return scan_duplicate_images(
        source_dir=source_dir,
        recursive=bool(recursive),
        threshold=int(threshold),
        limit=int(limit),
        max_files=int(max_files),
        max_images=int(max_images),
        bucket_prefix_length=int(bucket_prefix_length),
        max_bucket_size=int(max_bucket_size),
    )


if __name__ == "__main__":
    try:
        raw_input = sys.stdin.read()
        input_data = json.loads(raw_input) if raw_input else {}

        data = run(input_data)

        emit_final("图片重复扫描完成", data)

    except Exception as error:
        emit_error(error)
import os
import hashlib
from PIL import Image
import imagehash
from collections import defaultdict
from datetime import datetime
from concurrent.futures import ProcessPoolExecutor, as_completed  # 修改：导入as_completed
from tqdm import tqdm


class ImageDedupe:
    def __init__(self, file_path):
        self.file_path = file_path
        self.hash_dict = defaultdict(list)
        print(f"扫描目录: {self.file_path}")

    def get_image_hash(self, file_path):
        """计算单张图片的哈希值（支持多进程调用）"""
        try:
            with Image.open(file_path) as img:
                img = img.convert('RGB')
                return str(imagehash.phash(img, 8)), file_path
        except Exception as e:
            print(f"处理失败: {file_path} - {e}")
            return None, file_path

    def dedupe_image(self, max_workers=None, dry_run = True):
        """多进程扫描并去重"""
        image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.webp', '.tiff'}
        image_paths = []

        # 收集所有图片路径
        for root, _, files in os.walk(self.file_path):
            for filename in files:
                if os.path.splitext(filename)[1].lower() in image_extensions:
                    image_paths.append(os.path.join(root, filename))

        print(f"找到 {len(image_paths)} 张图片，开始多进程计算哈希...")

        # 使用进程池并行计算哈希
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            # 使用tqdm显示进度条
            futures = {executor.submit(self.get_image_hash, path): path for path in image_paths}
            for future in tqdm(as_completed(futures), total=len(image_paths), desc="计算哈希"):  # 修改：去掉concurrent.
                img_hash, file_path = future.result()
                if img_hash:
                    self.hash_dict[img_hash].append(file_path)

        self.delete_old_image(dry_run = dry_run)

    def delete_old_image(self, dry_run=False):
        """删除旧图片（基于文件大小保留最大的图片，大小相同则保留任意一个）"""
        total_deleted = 0
        for img_hash, paths in self.hash_dict.items():
            if len(paths) > 1:
                print(f"\n重复组 ({len(paths)}张):")
                # 按文件大小排序（从小到大）
                paths.sort(key=lambda p: os.path.getsize(p))

                # 计算每个文件的大小
                sizes = [os.path.getsize(p) for p in paths]
                max_size = max(sizes)
                max_size_count = sizes.count(max_size)

                for i, path in enumerate(paths):
                    size = os.path.getsize(path)
                    size_str = f"{size / 1024:.2f} KB" if size < 1024 * 1024 else f"{size / (1024 * 1024):.2f} MB"

                    # 判断是否为要保留的文件
                    is_largest = size == max_size
                    is_last_largest = is_largest and i == len(paths) - 1
                    is_only_largest = is_largest and max_size_count == 1

                    status = "✅ 保留" if (is_last_largest or is_only_largest) else "❌ 删除"
                    print(f"  {i + 1}. {path} - 文件大小: {size_str} - {status}")

                # 确定要保留的文件索引（最后一个最大的文件）
                keep_index = len(paths) - 1
                while keep_index > 0 and os.path.getsize(paths[keep_index]) == os.path.getsize(paths[keep_index - 1]):
                    keep_index -= 1  # 向前查找，直到找到不同大小的文件或第一个文件

                # 删除除保留文件外的其他文件
                for i, path in enumerate(paths):
                    if i != keep_index:
                        if not dry_run:
                            print(f"  执行删除: {path}")
                            try:
                                os.remove(path)
                                total_deleted += 1
                            except Exception as e:
                                print(f"  ❗ 删除失败: {e}")
                        else:
                            print(f"  模拟删除: {path}")

        print(f"\n共删除 {total_deleted} 张重复图片")

        print(f"\n操作完成！共删除 {total_deleted} 张旧图片")
        if not dry_run:
            print("⚠️ 注意：当前为预览模式，未实际删除文件。取消dry_run=True以执行。")


if __name__ == '__main__':
    image_dedupe = ImageDedupe(r'D:\新建文件夹\Picture')
    image_dedupe.dedupe_image(dry_run = False)

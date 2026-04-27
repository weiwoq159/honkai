import os
from pathlib import Path


def move_file(folders):
    file_path = Path(folders) / 'small'
    file_path.mkdir(parents=True, exist_ok=True)
    print(f"目标文件夹已创建: {file_path}")

    current = 0
    total_files = 0
    moved_files = []

    # 第一遍扫描：统计文件总数
    for root, _, files in os.walk(folders):
        total_files += len(files)

    print(f"开始处理 {total_files} 个文件...")

    # 第二遍扫描：移动小文件
    for root, _, files in os.walk(folders):
        for filename in files:
            full_path = os.path.join(root, filename)
            relative_path = os.path.relpath(full_path, folders)

            try:
                size_mb = os.path.getsize(full_path) / (1024 * 1024)
            except OSError as e:
                print(f"警告: 无法获取文件 {relative_path} 的大小 - {e}")
                continue

            if size_mb < 0.2:
                new_path = os.path.join(file_path, filename)

                # 处理文件重名情况
                if os.path.exists(new_path):
                    base, ext = os.path.splitext(filename)
                    counter = 1
                    while os.path.exists(os.path.join(file_path, f"{base}_{counter}{ext}")):
                        counter += 1
                    new_path = os.path.join(file_path, f"{base}_{counter}{ext}")

                try:
                    os.rename(full_path, new_path)
                    current += 1
                    moved_files.append(relative_path)
                    print(
                        f"[{current}/{total_files}] 已移动: {relative_path} -> small/{os.path.basename(new_path)} ({size_mb:.2f} MB)")
                except OSError as e:
                    print(f"错误: 无法移动文件 {relative_path} - {e}")

    print(f"\n处理完成!")
    print(f"共扫描: {total_files} 个文件")
    print(f"已移动: {current} 个小文件 (< 0.2 MB)")
    print(f"目标路径: {file_path}")

    if moved_files:
        print("\n移动的文件列表:")
        for file in moved_files:
            print(f"  - {file}")


if __name__ == '__main__':
    move_file(r'D:\新建文件夹\Picture')
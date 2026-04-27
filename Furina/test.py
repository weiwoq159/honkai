# import os
# import requests
# from bs4 import BeautifulSoup

# def fetch_and_download_images(url, dest_folder=r'D:\Image\downloaded_images'):
#     # 创建保存目录
#     os.makedirs(dest_folder, exist_ok=True)

#     # 请求页面
#     resp = requests.get(url)
#     resp.raise_for_status()
#     soup = BeautifulSoup(resp.text, "html.parser")

#     # 提取所有 img 标签
#     img_tags = soup.find_all("img")
#     img_urls = []

#     for img in img_tags:
#         img_url = img.get("data-src") or img.get("src")
#         if img_url:
#             img_urls.append(img_url)

#     print(f"共发现 {len(img_urls)} 张图片，开始下载...")

#     for i, img_url in enumerate(img_urls, start=1):
#         try:
#             img_resp = requests.get(img_url, timeout=10)
#             img_resp.raise_for_status()

#             # 提取文件名
#             filename = os.path.basename(img_url.split("?")[0])
#             if not filename.lower().endswith((".jpg", ".jpeg", ".png", ".gif", ".webp")):
#                 filename = f'image_{i}.jpg'

#             # 保存图片
#             file_path = os.path.join(dest_folder, filename)
#             with open(file_path, "wb") as f:
#                 f.write(img_resp.content)
#             print(f"✅ 已保存: {file_path}")
#         except Exception as e:
#             print(f"❌ 下载失败: {img_url}，原因: {e}")

# if __name__ == '__main__':
#     # target_url = 'https://happy.5ge.net/archives/3899.html'
#     target_url = 'https://happy.5ge.net/archives/5745.html'
#     fetch_and_download_images(target_url)

import time
from PIL import Image
import imagehash
import os

def process_image(path):
    print(f"\n📂 正在处理: {path}")
    size_mb = os.path.getsize(path) / (1024 * 1024)
    print(f"文件大小: {size_mb:.2f}MB")

    # Step 1: 打开图片
    t1 = time.time()
    img = Image.open(path).convert("RGB")
    t2 = time.time()
    print(f"🧾 open: {t2 - t1:.4f}s")

    # Step 2: 判断尺寸并 resize 到 1024
    w, h = img.size
    print(f"📏 尺寸: {w}x{h}")
    if w > 2000 or h > 2000:
        img = img.resize((1024, 1024))
    t3 = time.time()
    print(f"🔧 resize_if_large: {t3 - t2:.4f}s")

    # Step 3: 缩略图
    thumbnail = img.copy()
    thumbnail.thumbnail((512, 512))
    t4 = time.time()
    print(f"🖼 thumbnail(512): {t4 - t3:.4f}s")

    # Step 4: resize_exact(32×32)
    resized = thumbnail.resize((32, 32))
    t5 = time.time()
    print(f"📐 resize_exact(32x32): {t5 - t4:.4f}s")

    # Step 5: 计算 hash
    hash_val = imagehash.phash(resized)  # 你也可以用 average_hash 等
    t6 = time.time()
    print(f"🔐 hash: {t6 - t5:.4f}s")

    print(f"📌 总耗时: {t6 - t1:.4f}s")
    print(f"🧬 哈希: {hash_val}")

if __name__ == "__main__":
    # 你的图片路径，替换为实际图片
    process_image(r"D:\\Image\\Picture\\1735122290028(1).png")

# from PIL import Image
# import os
# from PIL import ImageFilter
#
# def generate_icons(input_path):
#     # 输出目录
#     output_dir = "./"
#     os.makedirs(output_dir, exist_ok=True)
#
#     # 打开原图
#     img = Image.open(input_path)
#
#     # 要生成的尺寸和文件名
#     sizes = [
#         (32, 32, "32x32.png"),
#         (128, 128, "128x128.png"),
#         (256, 256, "128x128@2x.png"),  # @2x 代表 128x128 的 2 倍尺寸
#     ]
#
#     for width, height, filename in sizes:
#         resized_img = img.resize((width, height), Image.Resampling.LANCZOS)
#         save_path = os.path.join(output_dir, filename)
#         resized_img.save(save_path)
#         print(f"Saved: {save_path}")
#
# # 示例用法
# generate_icons("./logo.png")

from PIL import Image

def png_to_ico(input_png, output_ico):
    img = Image.open(input_png)
    # 你可以传入多个 size，生成多分辨率的 .ico 文件
    img.save(output_ico, format='ICO', sizes=[(32, 32), (64, 64), (128, 128), (256, 256)])

png_to_ico("logo.png", "icon.ico")

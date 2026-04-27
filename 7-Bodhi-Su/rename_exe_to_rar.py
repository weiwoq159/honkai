import os
from pathlib import Path
import rarfile


def rename_exe_to_rar(file_path):
    for root, dirs, files in os.walk(file_path):
        for file in files:
            file_src = Path(root, file)
            if file_src.suffix == '.exe':
                os.rename(file_src, file_src.with_suffix('.rar'))

def unzip_file(file_path):
    for root, dirs, files in os.walk(file_path):
        for file in files:
            file_src = Path(root, file)
            print(file_src)
            if file_src.suffix == '.rar':
                with rarfile.RarFile(file_src) as rar_ref:
                    rar_ref.setpassword(1234)
                    rar_ref.extractall(path=file_path)


if __name__ == '__main__':
    unzip_file('D:\新建文件夹\g~光│渊.2023')
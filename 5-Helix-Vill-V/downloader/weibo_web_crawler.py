import json
from pathlib import Path
import requests
import ast
from urllib.parse import urlparse
from utils.database import HelixDatabase
from utils.urls import Urls
from config.index import config
import os
from datetime import datetime, timezone


class HelixWeiboCrawler:
    def __init__(self, url):
        self.uid = self.format_url(url)
        print(self.uid, 123)
        self.database = HelixDatabase()
        self.urls = Urls()
        self.current_page = 0
        self.screen_name = ''
        self.init_user_table()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.5845.97 Safari/537.36 Core/1.116.518.400 QQBrowser/19.2.6463.400',
            'X-Xsrf-Token': 'zcQ3lLoDfP_IWKC3Ruldi9D2',
            "referer": "https://weibo.com/"
        }
        pass

    def convert_time_format(self, time_str):
        # 定义原始时间格式
        original_format = '%a %b %d %H:%M:%S %z %Y'

        # 将字符串转换为 datetime 对象
        dt = datetime.strptime(time_str, original_format)

        # 转换为指定的年月日格式（例如：2024-01-10）
        formatted_date = dt.strftime('%Y-%m-%d')

        return formatted_date

    def format_url(self, url):
        parsed_url = urlparse(url)
        path_segments = parsed_url.path.strip('/').split('/')
        if len(path_segments) >= 2 and path_segments[0] == 'u':
            return path_segments[1]
        return None

    def init_user_table(self):
        res = requests.get(self.urls.WEIBO_USER_INFO, params={'uid': self.uid}, cookies=config.weibo_cookies)
        screen_name = res.json().get('data', {}).get('user',{}).get('screen_name', '')
        self.screen_name = screen_name
        if res.status_code == 200:
            self.database.add_weibo_user(self.uid, screen_name)

    def download_all(self):
        print(f"📥 开始抓取 UID={self.uid} 的微博数据...")
        while True:
            print(f"\n⏳ 正在请求第 {self.current_page} 页...")  # 打印当前页数

            res = requests.get(
                self.urls.WEIBO_BLOG_LIST,
                params={
                    'uid': self.uid,
                    'page': self.current_page,
                    'feature': 0
                },
                cookies=config.weibo_cookies,
                headers=self.headers
            )

            if res.status_code == 200:
                blog_list = res.json().get('data', {}).get('list', [])
                blog_count = len(blog_list)
                print(f"🔍 获取到 {blog_count} 条微博")  # 打印当前页获取到的微博数量

                if blog_count > 0:
                    for blog_item in blog_list:
                        text_raw = blog_item.get('text_raw')
                        blog_id = blog_item.get('idstr')
                        dt_obj = datetime.strptime(blog_item.get('created_at'), "%a %b %d %H:%M:%S %z %Y")
                        timestamp_ms = int(dt_obj.timestamp() * 1000)
                        blog_user_id = str(blog_item.get('user', {}).get('id'))

                        if blog_user_id == self.uid or (blog_user_id != self.uid and self.screen_name in text_raw):
                            if 'pic_infos' in blog_item:
                                pic_infos = blog_item.get('pic_infos')
                                arr = []
                                for key, value in pic_infos.items():
                                    largest_url = value.get('largest').get('url')
                                    arr.append(largest_url)

                                print(f"⬇️ 保存微博 ID={blog_id} (图片数: {len(arr)})")  # 打印当前微博信息
                                self.database.insert_weibo_blog_item(blog_id, self.uid, timestamp_ms, str(arr),
                                                                     text_raw)

                    self.current_page += 1  # 翻页
                else:
                    print("✅ 已抓取完所有微博！")
                    break
            else:
                print(f"❌ 请求失败！Status Code: {res.status_code}")
                break

        print("\n📁 开始下载文件...")
        self.download_file()  # 调用下载方法

    def download_file(self):
        blog_list = self.database.select_weibo_blog_list_by_uid(self.uid)
        for blog in blog_list:
            (blog_id, uid,text_raw, created_at, image_list ) = blog
            image_list = ast.literal_eval(image_list)
            for image in image_list:
                self.download_image(image, created_at)

    def get_pic_name_from_url(self, url):
        path = urlparse(url).path
        return os.path.basename(path)

    def download_image(self, src, created_at):
        timestamp = created_at // 1000
        dt_utc = datetime.fromtimestamp(timestamp, tz=timezone.utc)

        # 转换为本地时间（自动处理时区）
        dt_local = dt_utc.astimezone()

        # 格式化为字符串
        time_str = dt_local.strftime("%Y-%m-%d-%H_%M_%S")

        file_name = self.get_pic_name_from_url(src)
        folder_path = Path(f'../download/{self.screen_name}/images/')
        folder_path.mkdir(parents=True, exist_ok=True)
        file_path = folder_path / f'{time_str}-{file_name}'
        if os.path.exists(file_path):
            print(f"文件 {file_path} 已存在，跳过下载。")
            return
        try:
            print(f"开始下载：{src}")
            response = requests.get(src, headers=self.headers, stream=True, cookies=config.weibo_cookies)
            response.raise_for_status()
            with open(file_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        file.write(chunk)
            print(f"下载完成：{file_path}")

        except requests.exceptions.RequestException as e:
            print(f"下载失败（URL：{src}）：{e}")
        except OSError as e:
            print(f"文件写入失败：{e}")
    def select_blog(self):
        lists = self.database.select_weibo_blog_item_by_uid(self.uid, '安排')
        print(lists)
if __name__ == '__main__':
    # crawler = HelixWeiboCrawler('https://weibo.com/u/1909576453') # 风眠眠
    # crawler.download_all()
    # crawler = HelixWeiboCrawler('https://weibo.com/u/6400306290') # 走路摇ZLY
    crawler = HelixWeiboCrawler('https://weibo.com/u/1868515735') #小南宫
    # crawler = HelixWeiboCrawler('https://weibo.com/u/1009328584?tabtype=album') #小南宫

    crawler.download_all()
    # crawler.download_file()

    # crawler.select_blog()

# 06Z922Cgy1i1qeg3vq0nj33ls5eokjs.jpg
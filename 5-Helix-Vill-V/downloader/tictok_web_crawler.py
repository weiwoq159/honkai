import json
from urllib.parse import urlparse
import requests
from utils.index import Utils
from utils.urls import Urls
from config.index import config
from utils.database import HelixDatabase
import time
from utils.helix_log import HelixLogger
from pathlib import Path
import re
import ast
from tqdm import tqdm

helix_douyin_logger = HelixLogger()

class HelixDouyinCrawler:
    def __init__(self, url) -> None:
        self.parsed_url = urlparse(url)
        self.sec_user_id = self.get_user_id()
        if not self.sec_user_id:
            helix_douyin_logger.error("无法从URL中提取用户ID")
            raise ValueError("无法从URL中提取用户ID")
        self.urls = Urls()
        self.database = HelixDatabase()
        self.get_user_detail()
        self.user_name = ''
        print('123')
    def get_user_id(self):
        """从URL路径中提取用户ID"""
        path_segments = self.parsed_url.path.strip('/').split('/')
        if len(path_segments) >= 2 and path_segments[0] == 'user':
            return path_segments[1]
        return None

    def get_user_detail(self):
        try:
            url = self.urls.USER_DETAIL + Utils().getXbogus(f'sec_user_id={self.sec_user_id}&device_platform=webapp&aid=6383')
            res = requests.get(url, headers=config.douyin_headers)
            res.raise_for_status()
            user_detail = res.json().get('user', {})
            user_id = user_detail.get('sec_uid')
            user_name = user_detail.get('nickname')
            self.user_name = user_name
            if user_id and user_name:
                self.database.add_user(user_id=user_id, user_name=user_name)
            else:
                helix_douyin_logger.warning("未获取到完整的用户信息")
        except requests.RequestException as e:
            helix_douyin_logger.error(f"获取用户详情时发生请求错误: {e}")
        except json.JSONDecodeError as e:
            helix_douyin_logger.error(f"解析用户详情JSON数据时发生错误: {e}")

    def get_user_all_videos(self, count=35, number=0, end_time='now', start_time=None):
        if end_time == 'now':
            end_time = time.strftime("%Y-%m-%d")
        if not start_time:
            start_time = "1970-01-01"
        max_cursor = 0
        headers = config.douyin_headers
        total_videos = 0

        try:
            while True:
                print(f'----------{total_videos}---------')
                url = self.urls.USER_POST + Utils().getXbogus(
                    f'sec_user_id={self.sec_user_id}&count={count}&max_cursor={max_cursor}&device_platform=webapp&aid=6383')
                res = requests.get(url=url, headers=headers)
                res.raise_for_status()

                aweme_list = res.json().get('aweme_list', [])
                if not aweme_list:
                    helix_douyin_logger.info(f'视频获取完成，总共：{total_videos}')
                    break

                new_video_count = 0
                for aweme in aweme_list:
                    item_id = aweme.get('aweme_id')
                    if self.database.select_aweme_item(item_id):
                        continue  # 如果视频已存在，跳过
                    desc = aweme.get('desc') if aweme.get('desc') else str(time.time())
                    create_time = aweme.get('create_time')
                    video_info = aweme.get('video')
                    if video_info:
                        bit_rates = video_info.get('bit_rate')
                        if bit_rates:
                            bit_rate = max(bit_rates, key=lambda x: x["play_addr"]["data_size"])
                            video_url = bit_rate.get('play_addr').get('url_list')[0]
                            print(item_id, self.sec_user_id, desc, create_time, video_url, 'videos')
                            self.database.insert_aweme_item(item_id, self.sec_user_id, desc, create_time, video_url, 'videos')
                        else:
                            image_list = [item["url_list"][0] for item in aweme.get('images', [])]
                            self.database.insert_aweme_item(item_id, self.sec_user_id, desc, create_time, str(image_list), 'images')
                    new_video_count += 1

                if new_video_count == 0:
                    helix_douyin_logger.info(f'未发现新视频，视频获取完成，总共：{total_videos}')
                    break

                self.save_json(f'{max_cursor}.json', res.json())
                max_cursor = res.json().get('max_cursor', None)
                total_videos += len(aweme_list)

        except requests.RequestException as e:
            helix_douyin_logger.error(f"获取用户视频时发生请求错误: {e}")
        except json.JSONDecodeError as e:
            helix_douyin_logger.error(f"解析用户视频JSON数据时发生错误: {e}")
        self.download_video()
    def download_video(self):
        aweme_list = self.database.select_aweme_list(self.sec_user_id)
        current = 1
        print(f'总共：{len(aweme_list)}条')
        (user_name, ) = self.database.select_user_name_by_id(self.sec_user_id)[0]
        video_path = Path(f'../download/{user_name}/videos')
        image_path = Path(f'../download/{user_name}/images')
        video_path.mkdir(parents=True, exist_ok=True)  # parents=True自动创建父目录
        image_path.mkdir(parents=True, exist_ok=True)
        invalid_chars = r'[\\/:*?"<>|]'

        for aweme in tqdm(aweme_list, desc="总进度", unit="个"):
            (aweme_id, user_id, desc, create_time, aweme_url, aweme_type) = aweme
            date_str = time.strftime("%Y-%m-%d", time.localtime(create_time))
            file_name = desc.split('#')[0] if desc.split('#')[0] != '' else desc.split('#')[1]
            video_file_name = f"{date_str}-{file_name}"
            cleaned_text = re.sub(invalid_chars, '', video_file_name)
            print('正在下载：', cleaned_text)
            if aweme_type == 'videos':
                self.save_file(video_path, cleaned_text, aweme_url, aweme_type)
            else:
                index = 0
                aweme_url = ast.literal_eval(aweme_url)
                with tqdm(aweme_url, desc=f"图片 {cleaned_text}", unit="张", leave=False) as pbar:
                    for i, url_item in enumerate(pbar):
                        self.save_file(image_path, f'{cleaned_text}{i}', url_item, aweme_type)
                        pbar.set_postfix(file=f"{cleaned_text}{i}")
            current += 1

    def save_file(self, video_file_path, video_file_name, file_url, aweme_type):
        headers = config.douyin_headers
        res = requests.get(file_url, headers=headers)
        ext = 'mp4' if aweme_type == 'videos' else 'jpg'
        with open(video_file_path / Path(f"{video_file_name}.{ext}"), 'wb') as f:
            for chunk in res.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)


    @staticmethod
    def save_json(name, jsons):
        try:
            with open(name, 'w', encoding='utf-8') as f:
                json.dump(jsons, f, ensure_ascii=False, indent=4)
        except IOError as e:
            helix_douyin_logger.error(f"保存JSON文件时发生错误: {e}")

if __name__ == "__main__":
    url = 'https://www.douyin.com/user/MS4wLjABAAAAsPd6gdI_ZDATS8xW-qbduwBGNQKVlqClPQksZ3vg6BQ?from_tab_name=main'
    # url = 'https://www.douyin.com/user/MS4wLjABAAAAXn-GyjbmW_K5tkt58dhYKUgOGmxCYjkUHozRkIHBcO0?from_tab_name=main'
    try:
        downloader = HelixDouyinCrawler(url)
        downloader.get_user_all_videos()
    except ValueError as e:
        print(f"初始化爬虫时发生错误: {e}")


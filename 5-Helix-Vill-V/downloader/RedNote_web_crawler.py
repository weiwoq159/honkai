from pathlib import Path
from urllib.parse import urlparse, parse_qs
from utils.database import HelixDatabase
import requests
from config.index import config
import json
from PIL import Image
import pillow_heif
import os
pillow_heif.register_heif_opener()


class HelixRedNoteCrawler:
    def __init__(self, url):
        self.uid = self.get_uid(url)
        self.nickname = ''
        self.database = HelixDatabase()
        self.fetch_user_info()
        self.headers = {

        }
    @staticmethod
    def get_uid(url):
        path_segments = urlparse(url).path.split('/')
        uid = path_segments[-1] if path_segments[-1] else path_segments[-2]
        return uid

    def get_note_list(self):
        pass

    def fetch_user_info(self):
        # res = requests.get(f'https://edith.xiaohongshu.com/api/sns/v3/user/info?cny_source=other&profile_page_head_exp=1&user_id={self.uid}', cookies=config.REDnote_cookies, headers=config.REDnote_headers)
        # print(res.json())
        # with open('./123.json', 'w', encoding='utf-8') as f:
        #     json.dump(res.json(), f, ensure_ascii=False, indent=4)
        with open('./123.json', 'r', encoding='utf-8') as f:
            response = json.loads(f.read())
        if response.get('success', False):
            user_info = response.get('data', {})
            self.uid = user_info.get('userid')
            self.nickname = user_info.get('nickname')
            self.database.upsert_user_details(username=user_info.get('nickname'), REDnote_id=user_info.get('userid'))


    def fetch_image_note_list(self):
        payload = {
            "num": "20",
            "page": "2",
            "page_size": "15",
            "pin_note_id": "",
            "source": "user_profile",
            "sub_tag_id": "",
            "use_cursor": "1",
            "user_id": self.uid
        }
        headers = {
            "Host": "edith.xiaohongshu.com",
            "Connection": "Keep-Alive",
            "x-legacy-fid": "",
            "User-Agent": "discover/8.84 (iPhone; iOS 18.5; Scale/3.00) Resolution/1290*2796 Version/8.84 Build/8840703 Device/(Apple Inc.;iPhone16,2) NetType/WiFi",
            "xy-direction": "90",
            "x-xray-traceid": "cb88e2c92e3394dabeaacfcfb14b8587",
            "xy-scene": "point=364&fs=0",
            "x-mini-mua": "eyJhIjoiRUNGQUFGMDIiLCJjIjoxNDI1LCJrIjoiMWFlYzVmYzFhNzA0MDg0NjU0OWM5NTNkYjFiZjYyYjQ0OTY0YTA3YWEyYTBhNjQ1NmYyMjQwNGM1MDVhNmY1OSIsInAiOiJpIiwicyI6IjY5YzJkMDNhYWFjY2Y0OGU1OTcyYjg5ZDMyYzhlY2EzIiwidSI6IjAwMDAwMDAwYjYyMThiMzVmNTk0N2M5Mzc3ZjY5MGY1OTgyMTUyOWEiLCJ2IjoiMi4xLjM0In0.I5aP_rfhwQEXW-ni9Kvpm0ztFY90c-YQ6Nz68V7YYyUnIGZUez4zTn1dvp8DFtIAHmMOPeoEmoCwTDtNr9LzaOkRpipaGJHk8DasbGdaPeY2K-S5-BUj_8BPseGuZfxTtbt5JGSYzyDgWwRbzicclqj_D88bg3u7z4byzg_VytR2SUxf5Fc2s9edOmvzReP6dHORbchkB4Az9y12nZIIplp_tY7vpQ53haZiVvuuaPZd_90BjMI8CzkvnYIc8KyPUhf4wM3L4v3uLKJWvIvr87YkOXQLh59re5g-43dc9HV1JkT9Sy2ZV8fKzi0uxnzHBDJmlRJKZED12hA59GGxPgiQkfkzPm1iRj-SZZI6rCEEPP3qAwdI-kYkUod6-H28F65UGL0GP7bWsVTRuJIfMNkxvtt-57Im7WK-lCFX-GD4Ott2o0Kt-u_cejx3-7YZ0U4Qq9Aus2GD_BvdnT_3muVDUadp4q0nciZRFUS5UR1PR4TH_leNOZSHxnRg2HD-eZOUc4Q0uZLtQzL2_iSQAJi7AfzBwLAs2IowqcJEyTkqweY4GR_9gDJduSUgGFmqPtbdnz7nHqmTzM7BDFj-rw.",
            "X-B3-TraceId": "b7fd1caf286fe222",
            "x-mini-gid": "7c1ef9efa39055a89d4ec3389a2c6edcb90705f8473596fd77a70e5a",
            "Accept-Language": "zh-Hans-CN;q=1",
            "x-mini-s1": "AHMDAAAB71EHI1VEyRh9C+8npXiN+gdQpE/r60q54etniu7fCsdaE9xCpM90XkNb4xN1BdT7HkUujM0IJV0=",
            "x-legacy-did": "437CD34E-ADF7-4832-A0BB-BF22DAC254B0",
            "x-mini-sig": "02f09ea8c841eba1a8e58959dcaca6b9e68ffa2d611fbcf6c123dd30a3fca87e",
            "shield": "XYAAEAAgAAAAEAAABTAAAAUzUWEe4xG1IYD9/c+qCLOlKGmTtFa+lG434GeOFRRK5GxoPD6rVjOZ2Ji5ZYz8Qi389+oKJAYgw8Z2eKEMqH3i5k9OSTRmUF0BDcF25BMyL/JHW4",
            "X-Net-Core": "crn",
            "xy-platform-info": "platform=iOS&version=8.84&build=8840703&deviceId=437CD34E-ADF7-4832-A0BB-BF22DAC254B0&bundle=com.xingin.discover",
            "Accept-Encoding": "br;q=1.0, gzip;q=1.0, compress;q=0.5",
            "Mode": "gslb",
            "xy-common-params": "active_ctry=CN&app_id=ECFAAF02&auto_trans=0&build=8840703&channel=AppStore&deviceId=437CD34E-ADF7-4832-A0BB-BF22DAC254B0&device_model=phone&did=b7def8796fcc3e0095ce57383bc65825&dlang=zh&fid=&gid=7c1ef9efa39055a89d4ec3389a2c6edcb90705f8473596fd77a70e5a&holder_ctry=CN&identifier_flag=0&is_mac=0&lang=zh-Hans&launch_id=770032821&mlanguage=zh_cn&overseas_channel=0&platform=iOS&project_id=ECFAAF&sid=session.1714289400662640548249&t=1748349850&teenager=0&tz=Asia/Shanghai&uis=light&version=8.84",
            "X-raw-ptr": "0",
            "Accept": "*/*",
            "Referer": "https://app.xhs.cn/",
        }
        response = requests.get('https://edith.xiaohongshu.com/api/sns/v4/note/user/posted', headers=headers, cookies=config.REDnote_cookies, params=payload)
        print(response.json())
        # print(res.json())
        # with open('./223.json', 'w', encoding='utf-8') as f:
        #     json.dump(res.json(), f, ensure_ascii=False, indent=4)
        # with open('./223.json', 'r', encoding='utf-8') as f:
        #     response = json.loads(f.read())
        note_list = response.json().get('data', {}).get('notes', [])
        for note in note_list:
            if 'video_info_v2' not in note:
                title = note.get('display_title')
                print(title)
                desc = note.get('desc')
                note_id = note.get('id')
                images_list = [image.get('url_size_large') for image in note.get('images_list')]
                self.database.insert_Rednote_list(node_id=note_id, title=title, user_id=self.uid, desc=desc, create_time=note.get('create_time'), url=str(images_list), note_type='images')
                # current = 0
                # for images in images_list:
                #     self.download_image(images, f"{title}_{current}")
                #     current += 1

    def download_image(self, url, image_name):
        """下载HEIF图片并转换为PNG格式"""
        image_path = Path(f'../download/{self.nickname}/images')
        image_path.mkdir(parents=True, exist_ok=True)
        res = requests.get(url, stream=True)
        res.raise_for_status()  # 检查请求是否成功
        # 创建临时文件存储HEIF图片
        temp_heif_path =  image_path / f"{image_name}.heif"
        with open(temp_heif_path, 'wb') as f:
            for chunk in res.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

        # 转换HEIF为PNG
        png_path = image_path / f"{image_name}.png"
        try:
            with Image.open(temp_heif_path) as img:
                img.save(png_path, "PNG")
            print(f"成功转换并保存为: {png_path}")
            return png_path
        except Exception as e:
            print(f"转换失败: {e}")
            return None
        finally:
            # 清理临时HEIF文件
            import os
            if os.path.exists(temp_heif_path):
                os.remove(temp_heif_path)


if __name__ == '__main__':
    helix_redNote_crawler = HelixRedNoteCrawler('https://www.xiaohongshu.com/user/profile/56a4c0455e87e70b5889f0a1?xsec_token=YBqsFVNUXylM2_BSXxTa7wjeI_vl5Gdf-13HiaKlj-HZY=&xsec_source=app_share&xhsshare=WeixinSession&appuid=6534ddd0000000000301cf15&apptime=1748349408&share_id=4e4caddf8f304d01aa0bc0b69e1f03c6')
    helix_redNote_crawler.fetch_image_note_list()
    # 2.89 09/17 MWm:/ Y@m.dn 一起，行至海岸尽头 # 鸣潮守岸人 # 鸣潮  https://v.douyin.com/05k3ozcHiWo/ 复制此链接，打开Dou音搜索，直接观看视频！
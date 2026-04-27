import yaml
import requests
import random
from pathlib import Path



class ConfigData:
    def __init__(self):
        config_dic = self.get_yaml_config()
        self.ms_token = config_dic.get('cookies').get('msToken')
        self.ttwid = config_dic.get('cookies').get('ttwid')
        self.odin_tt = config_dic.get('cookies').get('odin_tt')
        self.passport_csrf_token = config_dic.get('cookies').get('passport_csrf_token')
        self.sid_guard = config_dic.get('cookies').get('sid_guard')
        self.ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'
        self.weibo_cookies = self.set_cookie(config_dic.get('weibo_cookies'))
        self.REDnote_cookies = self.set_cookie(config_dic.get('REDnote_cookies'))
        self.douyin_headers = {
            'User-Agent': self.ua,
            'referer': 'https://www.douyin.com/',
            'accept-encoding': None,
            'Cookie': f"msToken={self.ms_token}; ttwid={self.get_ttwid()};odin_tt={self.odin_tt};passport_csrf_token={self.passport_csrf_token};sid_guard={self.sid_guard}"
        }
        self.REDnote_headers = {
            "Host": "edith.xiaohongshu.com",
            "Connection": "Keep-Alive",
            "x-legacy-fid": "",
            "User-Agent": "discover/8.84 (iPhone; iOS 18.5; Scale/3.00) Resolution/1290*2796 Version/8.84 Build/8840703 Device/(Apple Inc.;iPhone16,2) NetType/WiFi",
            "xy-direction": "90",
            "x-xray-traceid": "cb88e2c92db394d94283eb48ab7e3b4a",
            "xy-scene": "point=364&fs=0",
            "x-mini-mua": "eyJhIjoiRUNGQUFGMDIiLCJjIjoxNDI0LCJrIjoiMWFlYzVmYzFhNzA0MDg0NjU0OWM5NTNkYjFiZjYyYjQ0OTY0YTA3YWEyYTBhNjQ1NmYyMjQwNGM1MDVhNmY1OSIsInAiOiJpIiwicyI6IjY5YzJkMDNhYWFjY2Y0OGU1OTcyYjg5ZDMyYzhlY2EzIiwidSI6IjAwMDAwMDAwYjYyMThiMzVmNTk0N2M5Mzc3ZjY5MGY1OTgyMTUyOWEiLCJ2IjoiMi4xLjM0In0.I5aP_rfhwQEXW-ni9Kvpm0ztFY90c-YQ6Nz68V7YYyUnIGZUez4zTn1dvp8DFtIAHmMOPeoEmoCwTDtNr9LzaOkRpipaGJHk8DasbGdaPeY2K-S5-BUj_8BPseGuZfxTtbt5JGSYzyDgWwRbzicclqj_D88bg3u7z4byzg_VytR2SUxf5Fc2s9edOmvzReP6dHORbchkB4Az9y12nZIIplp_tY7vpQ53haZiVvuuaPZd_90BjMI8CzkvnYIc8KyPUhf4wM3L4v3uLKJWvIvr87YkOXQLh59re5g-43dc9HV1JkT9Sy2ZV8fKzi0uxnzHBDJmlRJKZED12hA59GGxPgiQkfkzPm1iRj-SZZI6rCEEPP3qAwdI-kYkUod6-H28F65UGL0GP7bWsVTRuJIfMNkxvtt-57Im7WK-lCFX-GD4Ott2o0Kt-u_cejx3-7YZ0U4Qq9Aus2GD_BvdnT_3muVDUadp4q0nciZRFUS5UR1PR4TH_leNOZSHxnRg2HD-eZOUc4Q0uZLtQzL2_iSQAJi7AfzBwLAs2IowqcJEyTkqweY4GR_9gDJduSUgGFmqPtbdnz7nHqmTzM7BDFj-rw.",
            "X-B3-TraceId": "b7f1947b836c5a36",
            "x-mini-gid": "7c1ef9efa39055a89d4ec3389a2c6edcb90705f8473596fd77a70e5a",
            "Accept-Language": "zh-Hans-CN;q=1",
            "x-mini-s1": "AHIDAAABKzjL1PNJ7J0E/aul6qPtSvRFzJL4CAC0uoZzpdTiqgeDe65yPlcEs/rhK6Q+vurbaS+Hewt6BT8=",
            "x-legacy-did": "437CD34E-ADF7-4832-A0BB-BF22DAC254B0",
            "x-mini-sig": "b04033094fec93b77dd8fd63b9f51efbf70ff51c00c33969109b80b992808792",
            "shield": "XYAAEAAgAAAAEAAABTAAAAUzUWEe4xG1IYD9/c+qCLOlKGmTtFa+lG434GeOFRRK5GxoPD6rVjOZ2Ji5ZYz8Qi389+oKJAYgw8Z2eKEMqH3i5k9OTyhz+8IzH0JBB2nqp1W4Rt",
            "X-Net-Core": "crn",
            "xy-platform-info": "platform=iOS&version=8.84&build=8840703&deviceId=437CD34E-ADF7-4832-A0BB-BF22DAC254B0&bundle=com.xingin.discover",
            "Accept-Encoding": "br;q=1.0, gzip;q=1.0, compress;q=0.5",
            "Mode": "gslb",
            "xy-common-params": "active_ctry=CN&app_id=ECFAAF02&auto_trans=0&build=8840703&channel=AppStore&deviceId=437CD34E-ADF7-4832-A0BB-BF22DAC254B0&device_model=phone&did=b7def8796fcc3e0095ce57383bc65825&dlang=zh&fid=&gid=7c1ef9efa39055a89d4ec3389a2c6edcb90705f8473596fd77a70e5a&holder_ctry=CN&identifier_flag=0&is_mac=0&lang=zh-Hans&launch_id=770032821&mlanguage=zh_cn&overseas_channel=0&platform=iOS&project_id=ECFAAF&sid=session.1714289400662640548249&t=1748349850&teenager=0&tz=Asia/Shanghai&uis=light&version=8.84",
            "X-raw-ptr": "0",
            "Accept": "*/*",
            "Referer": "https://app.xhs.cn/",
        }

    def set_cookie(self, cookies):
        dic = {}
        for cookie in cookies.split('; '):
            try:
                key, value = cookie.split('=', 1)
                dic[key] = value
            except ValueError:
                print(f"无效的Cookie格式：{cookie}")
        return dic
    @staticmethod
    def get_yaml_config():
        yaml_path = Path(__file__).parent.parent / 'config.yml'
        try:
            with open(yaml_path, 'r', encoding='utf-8') as f:
                config_dict = yaml.safe_load(f)
                return config_dict
        except FileNotFoundError:
            print("未找到配置文件config.yml")
            return None

    @staticmethod
    def get_ttwid():
        url = 'https://ttwid.bytedance.com/ttwid/union/register/'
        data = '{"region":"cn","aid":1768,"needFid":false,"service":"www.ixigua.com","migrate_info":{"ticket":"","source":"node"},"cbUrlProtocol":"https","union":true}'
        res = requests.post(url=url, data=data)
        if res.status_code == 200:
            return res.cookies['ttwid']
        return None

    @staticmethod
    def generate_random_str(random_length=16):
        """
        根据传入长度产生随机字符串
        """
        random_str = ''
        base_str = 'ABCDEFGHIGKLMNOPQRSTUVWXYZabcdefghigklmnopqrstuvwxyz0123456789='
        length = len(base_str) - 1
        for _ in range(random_length):
            random_str += base_str[random.randint(0, length)]
        return random_str

config = ConfigData()
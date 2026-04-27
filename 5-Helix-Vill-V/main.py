import re
from urllib.parse import urlparse

from downloader.tictok_web_crawler import HelixDouyinCrawler

if __name__ == '__main__':
    url = 'https://www.douyin.com/user/MS4wLjABAAAAXn-GyjbmW_K5tkt58dhYKUgOGmxCYjkUHozRkIHBcO0?from_tab_name=main'
    parsed_url = urlparse(url)
    domain_patterns = {
        r'(?:www\.)?douyin\.com': 'douyin',
        r'(?:www\.)?bilibili\.com': 'bilibili'
    }
    crawler_mapping = {
        'douyin': HelixDouyinCrawler,
        # 'bilibili': BilibiliCrawler  # 可扩展其他平台
    }
    matched_platform = None
    for pattern, platform in domain_patterns.items():
        if re.search(pattern, parsed_url.netloc):
            matched_platform = platform
            break

    if matched_platform and matched_platform in crawler_mapping:
        crawler_class = crawler_mapping[matched_platform]
        crawler = crawler_class(parsed_url)
    else:
        print(f"不支持的平台: {parsed_url.netloc}")
    # 抖音 https://www.douyin.com/user/MS4wLjABAAAAXn-GyjbmW_K5tkt58dhYKUgOGmxCYjkUHozRkIHBcO0?from_tab_name=main
    # 抖音分享 4.82 Q@k.PK GiP:/ 04/18 勇士，准备好了吗 # 魔兽世界巫妖王终章版本上线 # 巫妖王线下破次元来袭  https://v.douyin.com/7dv3DerKdsA/ 复制此链接，打开Dou音搜索，直接观看视频！
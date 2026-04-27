import requests

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.5845.97 Safari/537.36 Core/1.116.541.400 QQBrowser/19.4.6579.400',
    'Referer': 'https://weibo.com/'
}

# url = 'https://image.baidu.com/search/down?url=https://fc.sinaimg.cn/large/3c2921c8ly1hdxsmwxhzyj23344mox6v.jpg'
# url = 'https://fc.sinaimg.cn/large/3c2921c8ly1hdxsmwxhzyj23344mox6v.jpg'
url = 'https://lz.sinaimg.cn/large/0076Aswbly1he9jpxzysnj31o02i0qb6.jpg'
# url = 'https://lz.sinaimg.cn/large/3c2921c8ly1hdxsmcsduwj23344mo7wm.jpg'
# url = 'https://wx1.sinaimg.cn/large/3c2921c8ly1hloqlqafjaj20wr1z0b29.jpg'

res = requests.get(url, headers=headers)
print(res)
with open(f"123.jpg", 'wb') as f:
    for chunk in res.iter_content(1024):
        f.write(chunk)
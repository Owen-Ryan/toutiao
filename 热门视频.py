import execjs
import requests
import time
from urllib.parse import urlencode
import urllib3
import pandas as pd
urllib3.disable_warnings()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36",
}
#url = "https://www.toutiao.com/api/pc/list/feed?offset=0&channel_id=94349549395&max_behot_time=0&category=pc_profile_channel&disable_raw_data=true&aid=24&app_name=toutiao_web";

cookies = {'tt_webid': '6649949084894053895'}
url = "https://www.toutiao.com/api/pc/list/feed?"
offset = '0'
a = 0
data = []
for i in range(4):
    params1 = {
        'offset': offset,
        "channel_id": "94349549395",
        "max_behot_time": "0",
        "category": "pc_profile_channel",
        'disable_raw_data': 'true',
        "aid": "24",
        "app_name": "toutiao_web",
    }
    start_url = url + urlencode(params1)
    with open('toutiao.js', 'r', encoding='utf-8') as f:
        encrypt = f.read()
        _signature = execjs.compile(encrypt).call('getSignature',start_url)

    params2 = {
        'offset':offset,
        "channel_id": "94349549395",
        "max_behot_time": "0",
        "category": "pc_profile_channel",
        'disable_raw_data': 'true',
        "aid": "24",
        "app_name": "toutiao_web",
        "_signature": _signature
    }
    start_url = url + urlencode(params2)
    #print(start_url)
    response = requests.get(start_url, headers=headers, verify=False)
    res = response.json()
    re = res.get('data')
    #print(re)
    #print(res.get('next').get('max_behot_time'))
    for i in re:
        #print(i.get('title'))
        # print(i.get('comment_count'))
        # print(i.get('read_count'))
        # print(i.get('media_name'))
        # print(i.get('video_like_count'))
        # print('--------------------------------------------------------------------')
        if len(i.get('title')) ==0:
            continue
        #print(i.get('behot_time'))
        else:
            print(i.get('title'))
            info = [i.get('title'), i.get('comment_count'), i.get('read_count'), i.get('video_like_count'), i.get('media_name')]
            data.append(info)
    a += 10
    offset = '{}'.format(a)
def save_news(data):
    df = pd.DataFrame(data, columns=['标题', '评论人数', '观看人数', '点赞人数', '作者'])
    df.to_csv('热门视频04.csv', index=None, encoding='utf_8_sig')
save_news(data)
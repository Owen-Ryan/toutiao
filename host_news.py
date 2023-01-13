import execjs  # 运行js文件
import requests
from urllib.parse import urlencode
import urllib3
from selenium import webdriver
from lxml import etree #解析网页
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
import pymysql
import emoji  # 将emoji表情转换成utf-8格式识别
import pandas as pd # 存储到csv文件
urllib3.disable_warnings()

class TouTiaoSpider(object):

    def __init__(self):
        self.driver = webdriver.Chrome()
        self.headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36",
        }
        self.cookies = {'tt_webid': '6649949084894053895'}#
        self.url = "https://www.toutiao.com/api/pc/list/feed?"
        self.start_url = 'https://www.toutiao.com'
        self.conn = pymysql.connect(
            host='127.0.0.1',
            port=3306,
            user='root',
            password='xixi',
            database='dms',
            charset='utf8mb4'
        )
        self.cursor = self.conn.cursor()
        self.max_behot_time = '{}'.format(int(time.time() - 201))
        self._signature = ''
        self.data = []
    # 获取链接的_signnature
    def get_signature(self):
        params = {
            "channel_id": "3189398996",
            "max_behot_time": self.max_behot_time,
            "category": "pc_profile_channel",
            'client_extra_params': '{"short_video_item": "filter"}',
            "aid": "24",
            "app_name": "toutiao_web"
        }
        respones_url = self.url + urlencode(params)
        with open('toutiao.js', 'r', encoding='utf-8') as f:
            encrypt = f.read()
            self._signature = execjs.compile(encrypt).call('getSignature', respones_url)
    # 运行主程序
    def run(self):
        for i in range(3):
            json_res = self.get_page()
            #time.sleep(1)
            self.get_news(json_res)
        #self.save_news()

    # 取得相关的文件ajax
    def get_page(self):
        self.get_signature()
        params = {
            "channel_id": "3189398996",
            "max_behot_time": self.max_behot_time,
            "category": "pc_profile_channel",
            'client_extra_params': '{"short_video_item": "filter"}',
            "aid": "24",
            "app_name": "toutiao_web",
            "_signature": self._signature
        }
        start_url = self.url + urlencode(params)
        print(start_url)
        try:
            respones = requests.get(start_url, headers=self.headers, cookies=self.cookies)
            if respones.status_code == 200:
                rs = respones.json()
                self.max_behot_time = '{}'.format(int(self.max_behot_time)-15)
                return rs
        except requests.ConnectionError:
            return None
    # 获取文章内容和发表时间
    def parse_detail_page(self,url):
        js_ = 'window.open("%s")' % url
        self.driver.execute_script(js_)
        self.driver.switch_to.window(self.driver.window_handles[1]) # 获取页面所有的句柄
        time.sleep(5)
        source = self.driver.page_source
        html = etree.HTML(source)
        publish_time = ''
        content = ""
        time_list = html.xpath('//div[@class="article-meta"]/span/text()')
        for i in time_list:
            publish_time += "".join(i)
        p_list = html.xpath(
            '//article[@class="syl-article-base tt-article-content syl-page-article syl-device-pc"]/p')  # 内容
        # print(p_list)
        if len(p_list) == 0:
            if len(html.xpath('//article[@tt-ignored-node="1"]')) != 0:
                p_list = html.xpath('//article[@tt-ignored-node="1"]/p')
        for p in p_list:
            text = ''
            if len(p.xpath('./text()')) != 0:
                text = p.xpath('./text()')
            elif len(p.xpath('./span/text()')) != 0:
                text = p.xpath('./span/text()')
            elif len(p.xpath('./span/span/text()')) != 0:
                text = p.xpath('./span/span/text()')
            else:
                text = p.xpath('//p/text()')
            # print(text)
            content += "".join(text)
        self.driver.close()
        self.driver.switch_to.window(self.driver.window_handles[0])
        #print(content)
        return content, publish_time
    # 获取文章的相关信息，并保存
    def get_news(self, json):
        json = json.get('data')
        #print(json)
        for text in json:
            #time.sleep(2)
            content, publish_time = self.parse_detail_page(text.get('display_url'))
            if text.get('comment_count') == None:
                comment_count = 0
            else:
                comment_count = text.get('comment_count')
            one_info = [emoji.demojize(text.get('title')), comment_count, text.get('digg_count'), text.get('read_count'), text.get('source'),
                        publish_time, text.get('display_url'), emoji.demojize(content)]
            #self.data.append(one_info)
            self.save(one_info)

    # 保存数据到 mysql数据库
    def save(self, data):
        print(data)
        sql = 'insert into toutiao(title,comment_count,digg_count,read_count,source,time,display_url,content) values(%s,%s,%s,%s,%s,%s,%s,%s);'
        self.cursor.execute(sql, (data[0], data[1], data[2], data[3], data[4], data[5], data[6], data[7]))
        self.conn.commit()
        # 关闭数据库
    # 可选择保存到CSV文件
    def save_news(self):
        df = pd.DataFrame(self.data, columns=['标题', '评论人数', '点赞人数', '观看人数', '来源', '发表时间', '新闻地址', '内容'])
        df.to_csv('thesis02.csv', index=None, encoding='utf_8_sig')
    # 关闭浏览器和数据库的链接
    def close(self):
        self.cursor.close()
        self.conn.close()
        self.driver.close()

if __name__ == '__main__':
    spider = TouTiaoSpider()
    spider.run()
    spider.close()
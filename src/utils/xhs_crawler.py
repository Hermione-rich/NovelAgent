from DrissionPage import ChromiumPage
import time
import pandas as pd
import csv
from paddleocr import PaddleOCR
from tqdm import tqdm
import os
import re
import requests
from pprint import pprint
from dotenv import load_dotenv

load_dotenv()
cookie = os.getenv("cookie")
referer = os.getenv("referer")
user_agent = os.getenv("user_agent")


class Xhs_crawler:
    def __init__(self, headers, url, re_title, re_img, save_img_path):
        self.headers = headers
        self.url = url
        self.save_img_path = save_img_path
        
        self.re_title = re_title
        self.re_img = re_img

    def fetch_response(self):
        response = requests.get(self.url, headers = headers)
        html = response.text
        return html
    def fetch_title(self):
        html = self.fetch_response()
        match = re.search(r'《(.*?)》', html)
        if match:
            return match.group(1)
        else:
            return "未命名作品"
    def fetch_img(self):
        html = self.fetch_response()
        img_path = re.findall(self.re_img, html)
        return img_path

    def get_save_dir(self):
        title = self.fetch_title()
        save_dir = os.path.join(self.save_img_path, title)
        os.makedirs(save_dir, exist_ok=True)
        return save_dir, title
    def download_img(self):
        img_path_list = self.fetch_img()
        save_dir, title = self.get_save_dir()

        saved_files = []
        for i, url in enumerate(tqdm(img_path_list, desc="下载图片")):
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    filename = f"img_{i}.jpg"
                    file_path = os.path.join(save_dir, filename)
                    with open(file_path, 'wb') as f:
                        f.write(response.content)
                    saved_files.append(file_path)
                else:
                    print(f"❌ 无法下载: {url}")
            except Exception as e:
                print(f"⚠️ 出错: {url}，错误信息: {e}")

        print(f"\n✅ 共下载 {len(saved_files)} 张图片，保存在 '{save_dir}'。")
        return saved_files
        
    
        


if __name__ == "__main__":
    headers = {
        'cookie': cookie,
        'referer': referer,
        'user-agent': user_agent
    }

    url= "https://www.xiaohongshu.com/explore/682ffa200000000022027567?xsec_token=ABIZd2sejQuarON_rxeZTFWcrqgc-uW0BNI_PeCC9Ugog=&xsec_source=pc_user"
    response = requests.get(url = url, headers= headers)
    html = response.text
    print(html)

    img = '<meta name="og:image" content="(.*?)">'
    title = '<meta name="description" content="(.*?)">'

    save_path = "./download_images"
    crawler = Xhs_crawler(headers, url, title, img, save_path)
    response = crawler.download_img()




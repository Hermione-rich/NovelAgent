import openai
import base64
# from langchain.chat_models import ChatOpenAI
# from langchain.prompts import PromptTemplate
from xhs_crawler import Xhs_crawler
import os
from dotenv import load_dotenv
import sys
from pprint import pprint
from collections import defaultdict
import json
from tqdm import tqdm

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
base_url = os.getenv("BASE_URL")

class JPG2TXT:
    def __init__(self, img_path :str, save_path: str, client, prompt):
        self.img_path = img_path
        self.save_path = save_path
        self.client = client
        self.prompt = prompt
        
    def encode_img(self, one_img_path:str):
        with open(one_img_path, 'rb') as f:
            return base64.b64encode(f.read()).decode('utf-8')
    
    def call_llm_with_image(self, base64_image:str):
        response = self.client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "user", "content": [
                {"type": "text", "text": self.prompt},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}"
                    }
                }
            ]}
        ],
        max_tokens=8192
    )
        return response.choices[0].message.content.strip()
    
    def fet_img(self):
        img_dict = defaultdict(list)
        for name in os.listdir(self.img_path):
            novel_path = os.path.join(self.img_path, name)
            if name not in img_dict:
                img_dict[name] = []
            for img in os.listdir(novel_path):
                img_path = os.path.join(novel_path,img)
                img_dict[name].append(img_path)
        return img_dict

    def process_novel(self):
        img_dict = self.fet_img()
        os.makedirs(self.save_path, exist_ok=True)
        for novel_name, img_list in tqdm(img_dict.items()):
            print(f"----- 正在处理小说 {novel_name} --------")
            novel_data = {
                "novel_name": novel_name,
                "content": []
            }

            for idx, img_path in enumerate(img_list):
                base64_img = self.encode_img(img_path)
                try:
                    content = self.call_llm_with_image(base64_img)
                    novel_data["content"].append({
                        "image_path": os.path.basename(img_path),
                        "content": content
                    })
                    print(f"✅ 已处理：{img_path}")
                except Exception as e:
                    print(f"❌ 错误处理：{img_path}，错误：{e}")
                    novel_data["content"].append({
                        "image_path": os.path.basename(img_path),
                        "content": f"识别失败：{str(e)}"
                    })
            json_path = os.path.join(self.save_path, f"{novel_name}.json")
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(novel_data, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    image_path = '/Users/afrathrone/Desktop/my_git/NovelAgent/src/utils/download_images'
    client = openai.OpenAI(api_key = api_key, base_url = base_url)
    processor = JPG2TXT(img_path = image_path,
                        save_path="./outputs",
                        client=client,
                        prompt="请识别并提取该图片中的中文内容")
    img_dict = processor.process_novel()
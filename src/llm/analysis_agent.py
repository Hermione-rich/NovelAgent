import os
import sys
from dataclasses import dataclass
from dotenv import load_dotenv
from openai import OpenAI
import pdfplumber
from docx import Document
import json

# 加载环境变量
load_dotenv()

@dataclass
class ConvertFormat:
    filepath: str
    filename: str
    
    def convert_tool(self):
        if self.filename.endswith(".txt"):
            print("已经是txt文件了")
            return os.path.join(self.filepath,self.filename)
        elif self.filename.endswith(".pdf"):
            return self.pdf_to_txt()
        elif self.filename.endswith(".doc"):
            return self.doc_to_txt()

    def pdf_to_txt(self):
        pdf_path = os.path.join(self.filepath,self.filename)
        with pdfplumber.open(pdf_path) as pdf:
            text = ""
            
            for page in pdf.pages:
                text += page.extract_text()
                text += "\n\n"
        
        txt_file_path = os.path.join(self.filepath,self.filename.replace(".pdf",".txt"))
        with open(txt_file_path, "w", encoding = "utf-8") as txt_file:
            txt_file.write(text)
        
        print(f"已转换文件: {self.filename} -> {txt_file_path}")
        os.remove(pdf_path)
        return txt_file_path
    
    
    def doc_to_txt(self):
        doc_path = os.path.join(self.filepath,self.filename)
        doc = Document(doc_path)
        
        # 提取文本
        text = ""
        for para in doc.paragraphs:
            text += para.text
            text += "\n\n"  
        
        txt_file_path = os.path.join(self.filepath, self.filename.replace(".docx", ".txt"))
        
 
        with open(txt_file_path, "w", encoding="utf-8") as txt_file:
            txt_file.write(text)
        
        print(f"已转换文件: {self.filename} -> {txt_file_path}")
        os.remove(doc_path)
        return txt_file_path

@dataclass
class NovelAnalysisAgent:
    name: str
    model: str
    prompt_path: str
    save_path: str
    novel_path: str
    novel_name: str
    client: OpenAI
    
    def convert_format(self):
        convert = ConvertFormat(self.novel_path,self.novel_name)
        file_path = convert.convert_tool()
        return file_path
    
    def load_novel(self) -> str:
        """加载小说文本"""
        load_path = self.convert_format()
        print(f"load_path is {load_path}")
        with open(load_path, "r", encoding="utf-8") as f:
            novel_text = f.read()
            return novel_text
        
    def analyze_novel(self, novel_text: str) -> dict:
        """分析小说的结构"""
        response = self.extract_story_structure(novel_text,self.client)
        
        if not os.path.exists(self.save_path):
            print(f"{self.save_path} 不存在，新建目录完成")
            os.makedirs(self.save_path)
        
        # 保存分析结果为 JSON 文件
        with open(f"{self.save_path}/{self.novel_name}.json", "w", encoding="utf-8") as json_file:
            json.dump(response, json_file, ensure_ascii=False, indent=4)
        return response
    
    def extract_story_structure(self, novel_text: str, client) -> dict:
        """从小说中提取起承转合结构"""
        with open(self.prompt_path, "r",encoding = "utf-8") as f:
            prompts= f.read()
            
        response = client.chat.completions.create(
                    model = self.model,
                    messages=[
                        {"role": "system", "content": "你是一个小说拆解的专家"},
                        {"role": "user", "content": f"{prompts}\n\n{novel_text}"}
                    ],
                    temperature=0.7,
                    max_tokens=512
                )
    
        
        return response.choices[0].message.content

# 主程序部分
if __name__ == "__main__":
    # 获取 API 密钥并初始化客户端
    api_key = os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("BASE_URL")
    
    # 创建代理实例
    save_path = r"/Users/afrathrone/Desktop/my_git/NovelAgent/output"
    prompt_path = r"../prompts/snow_flower.txt"
    client = OpenAI(api_key=api_key, base_url=base_url)
    # 设定小说路径
    novel_path = r"/Users/afrathrone/Desktop/my_git/NovelAgent/data/素材库/民俗"
    novel_name = "有哪些邪性的民间故事？ - 知乎(1).pdf"
    
    novel_agent = NovelAnalysisAgent(name="NovelAgent", 
                                     model="gpt-4o", 
                                     prompt_path= prompt_path,
                                     save_path = save_path,
                                     novel_path = novel_path,
                                     novel_name = novel_name,
                                     client = client)

    
    
    # 使用代理加载并分析小说
    novel_text = novel_agent.load_novel()
    
    # 保存结果到指定目录
    analysis_result = novel_agent.analyze_novel(novel_text)
    
    # 打印分析结果
    print(analysis_result)

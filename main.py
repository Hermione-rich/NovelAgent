from openai import OpenAI
import os
import random
from datetime import datetime
import json
from baidusearch.baidusearch import search
import asyncio
from dotenv import load_dotenv


load_dotenv()


api_key = os.getenv("OPENAI_API_KEY")
base_url = os.getenv("BASE_URL")
client = OpenAI(api_key = api_key,
                base_url = base_url)
response = client.chat.completions.create(
    model = "gpt-4o",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "跟我讲一个中文笑话吧。"}
    ],
    temperature=0.7,
    max_tokens=100
)

print(response.choices[0].message.content)
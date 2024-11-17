from pprint import pprint
import os
from openai import OpenAI

# api키는 환경변수에 이미 추가 했음.
# api_key = "sk-"
api_key = os.getenv("OPENAI_API_KEY")
# client = OpenAI() # 이것도 가능
client = OpenAI(api_key=api_key)

model = "gpt-4o"

messages = [
        {"role": "system", "content": "너는 하나금융 직원이야."},
        {"role": "user", "content": "증권을 구매하고 싶어 어디로 가야 하지?"},
    ]

response = client.chat.completions.create(model=model, messages=messages).model_dump()
pprint(response)

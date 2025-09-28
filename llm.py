from openai import OpenAI
import os
from dotenv import load_dotenv  

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "preferences.json")
BASE_URL = os.getenv("BASE_URL", "https://api.openai.com/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini")

client = OpenAI(
  base_url=BASE_URL,
  api_key=OPENAI_API_KEY,
)

def make_llm_call(prompt: str) -> str:
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content

def make_structured_call(messages: list[dict]) -> str:
    response = client.chat.completions.create(model=MODEL_NAME, messages=messages)
    return response.choices[0].message.content
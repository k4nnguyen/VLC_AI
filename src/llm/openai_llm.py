from openai import OpenAI
from src.llm.base_llm import BaseLLM

class OpenAILLM(BaseLLM):
    def __init__(self,
                api_key:str, 
                model:str = "gpt-4.1-mini", 
                base_url:str = "https://api.shopaikey.com/v1"
    ):
        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url,
            timeout=15.0, # Tránh bị treo nếu server phản hồi chậm
            max_retries=2 # Tự động thử lại nếu lỗi mạng
        )
        self.model = model
    def chat(self, 
            messages: list[dict]
    ) -> str:
        response = self.client.chat.completions.create(
            model = self.model,
            messages=messages,
            temperature=0
        )
        return response.choices[0].message.content
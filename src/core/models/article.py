# Chứa các điều (Điều - Khoản - Điểm)
from pydantic import BaseModel, Field

class Article(BaseModel):
    number: int
    title: str = ""
    raw_content: str = ""
    
    

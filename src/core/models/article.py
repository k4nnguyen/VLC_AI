# Chứa các điều (Điều - Khoản - Điểm)
from pydantic import BaseModel, Field
from src.core.models.clause import Clause

class Article(BaseModel):
    number: int
    title: str = ""
    raw_content: str = ""
    clauses: list[Clause] = Field(default_factory=list)
    

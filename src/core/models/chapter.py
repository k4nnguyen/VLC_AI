from pydantic import BaseModel, Field
from .article import Article

class Chapter(BaseModel):
    number: str
    title: str
    articles: list[Article] = Field(default_factory=list)

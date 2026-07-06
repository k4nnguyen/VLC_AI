from pydantic import BaseModel, Field
from .article import Article
from .section import Section
class Chapter(BaseModel):
    number: str
    title: str
    articles: list[Article] = Field(default_factory=list)
    sections: list[Section] = Field(default_factory=list)

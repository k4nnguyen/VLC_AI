from pydantic import BaseModel, Field
from src.core.models.article import Article


class Section(BaseModel):
    number: int
    title: str

    articles: list[Article] = Field(default_factory=list)
from pydantic import BaseModel, Field
from src.core.models.point import Point

class Clause(BaseModel):
    number: int
    content: str = ""
    points: list[Point] = Field(default_factory=list)
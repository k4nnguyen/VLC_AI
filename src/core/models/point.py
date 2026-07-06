from pydantic import BaseModel

class Point(BaseModel):
    label: str
    content: str
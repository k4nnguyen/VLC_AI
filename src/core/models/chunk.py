from pydantic import BaseModel, Field

class Chunk(BaseModel):
    chunk_id: str
    text: str
    metadata: dict = Field(default_factory=dict)
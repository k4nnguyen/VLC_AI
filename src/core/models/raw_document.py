# Cấu hình theo dạng Pydantic cho raw document
from datetime import datetime
from pathlib import Path
from pydantic import BaseModel, ConfigDict, Field

class RawDocument(BaseModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True
    )
    source: Path
    filename: str
    file_type: str 
    raw_text: str 
    loaded_at: datetime = Field(default_factory=datetime.now)
    
    
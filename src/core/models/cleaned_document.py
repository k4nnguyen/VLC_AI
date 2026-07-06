# Cấu hình dạng Pydantic cho cleaned document
from pydantic import BaseModel
from .raw_document import RawDocument

class CleanedDocument(BaseModel):
    raw_document: RawDocument
    cleaned_text: str 
    
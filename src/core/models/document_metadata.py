# Cấu hình theo dạng Pydantic cho Document metadata
from pydantic import BaseModel
from datetime import date

class DocumentMetadata(BaseModel):
    title: str | None = None
    document_number: str | None = None
    issuer: str | None = None
    issued_date: date | None = None
    effective_date: date | None = None
    language: str = "vi"
    version: str| None = None
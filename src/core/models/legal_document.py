from pydantic import BaseModel, Field
from .chapter import Chapter
from .document_metadata import DocumentMetadata

class LegalDocument(BaseModel):
    metadata: DocumentMetadata = Field(default_factory=DocumentMetadata)
    chapters: list[Chapter] = Field(default_factory=list)
    
    
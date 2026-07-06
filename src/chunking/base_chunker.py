from abc import ABC, abstractmethod
from src.core.models.legal_document import LegalDocument
from src.core.models.chunk import Chunk

class BaseChunker(ABC):
    @abstractmethod
    def chunk(self,document: LegalDocument) -> list[Chunk]:
        pass
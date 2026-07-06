from abc import ABC, abstractmethod
from src.core.models.cleaned_document import CleanedDocument
from src.core.models.legal_document import LegalDocument
class BaseParser(ABC):
    @abstractmethod
    def parse(self,document: CleanedDocument) -> LegalDocument:
        raise NotImplementedError
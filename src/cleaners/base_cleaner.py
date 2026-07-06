# Interface cho cac cleaner
from abc import ABC, abstractmethod
from src.core.models.cleaned_document import CleanedDocument
from src.core.models.raw_document import RawDocument

class BaseCleaner(ABC):
    @abstractmethod
    def clean(self,document: RawDocument) -> CleanedDocument:
        raise NotImplementedError
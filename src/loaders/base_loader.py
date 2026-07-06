# interface cho các loader
from abc import ABC, abstractmethod
from src.core.models.raw_document import RawDocument

class BaseLoader(ABC):
    @abstractmethod
    def load(self, file_path: str) -> RawDocument:
        """ Load document and return raw data"""
        raise NotImplementedError
    
    
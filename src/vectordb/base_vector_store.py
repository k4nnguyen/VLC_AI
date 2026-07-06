from abc import ABC, abstractmethod
from src.core.models.chunk import Chunk

class BaseVectorStore(ABC):
    @abstractmethod
    def add(self, chunks: list[Chunk]) -> None:
        pass

    @abstractmethod
    def search(self, query: str, k: int = 5):
        pass

    @abstractmethod
    def reset(self) -> None:
        pass
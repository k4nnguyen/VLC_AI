from chromadb import PersistentClient
from src.embeddings.embedding_model import EmbeddingModel
from src.core.models.chunk import Chunk
from src.vectordb.base_vector_store import BaseVectorStore

class ChromaStore(BaseVectorStore):
    def __init__(
        self,
        embedding_model: EmbeddingModel,
        db_path: str = "data/chroma",
        collection_name: str = "vlc_ai"
    ):
        self.embedding_model = embedding_model
        self.client = PersistentClient(path=db_path)
        self.collection = self.client.get_or_create_collection(
            name=collection_name
        )
        
    def add(self, chunks: list[Chunk]) -> None:
        """Add embeddings to ChromaDB"""

        embeddings = self.embedding_model.embed_documents(
            [chunk.text for chunk in chunks]
        )

        metadatas = [
            self._sanitize_metadata(chunk.metadata)
            for chunk in chunks
        ]

        self.collection.add(
            ids=[chunk.chunk_id for chunk in chunks],
            documents=[chunk.text for chunk in chunks],
            embeddings=embeddings,
            metadatas=metadatas
        )
    
    def search(
        self,
        query: str,
        k: int = 5
    ):
        """Vector search in chromadb"""
        embedding = self.embedding_model.embed_query(query)
        results = self.collection.query(
            query_embeddings=[embedding],
            n_results=k
        )
        return results
    
    def reset(self):
        """Delete and Re-create collection in chromadb"""
        name = self.collection.name
        self.client.delete_collection(name)
        self.collection = self.client.get_or_create_collection(
            name=name
        )
        
    def _sanitize_metadata(self, metadata: dict) -> dict:
        sanitized = {}

        for key, value in metadata.items():
            if value is None:
                sanitized[key] = ""
            elif isinstance(value, (str, int, float, bool)):
                sanitized[key] = value
            else:
                sanitized[key] = str(value)

        return sanitized
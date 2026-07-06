from sentence_transformers import SentenceTransformer
from src.embeddings.base_embedding import BaseEmbedding

class EmbeddingModel(BaseEmbedding):
    def __init__(self):
        self.model = SentenceTransformer(
            "intfloat/multilingual-e5-small"
        )
        
    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        texts = [f"passage: {text}" for text in texts]
        embeddings = self.model.encode(
            texts,
            normalize_embeddings=True,
            convert_to_numpy=True
        )
        return embeddings.tolist()

    def embed_query(self, text: str) -> list[float]:
        embedding = self.model.encode(
            f"query: {text}",
            normalize_embeddings=True,
            convert_to_numpy=True
        )
        return embedding.tolist()
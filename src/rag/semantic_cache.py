import json
import numpy as np
from pathlib import Path
from src.embeddings.embedding_model import EmbeddingModel

class SemanticCache:
    """
    TỐI ƯU 2: BỘ NHỚ ĐỆM NGỮ NGHĨA (SEMANTIC CACHING)
    Sử dụng Embedding để so sánh câu hỏi hiện tại với các câu hỏi cũ trong lịch sử.
    Nếu độ giống nhau (Cosine Similarity) > threshold (vd: 95%), trả về ngay kết quả 
    cũ mà không cần chạy GraphRAG hay gọi OpenAI (tốc độ xử lý còn ~0.1s).
    """
    def __init__(self, cache_file="data/processed/query_cache.json", threshold=0.95):
        self.cache_file = Path(cache_file)
        self.threshold = threshold
        self.embedder = EmbeddingModel()
        self.cache = self._load_cache()

    def _load_cache(self):
        if self.cache_file.exists():
            try:
                with open(self.cache_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return []

    def _save_cache(self):
        self.cache_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.cache_file, "w", encoding="utf-8") as f:
            json.dump(self.cache, f, ensure_ascii=False, indent=2)

    def _cosine_similarity(self, vec1, vec2):
        dot = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return dot / (norm1 * norm2)

    def get_cached_answer(self, question: str):
        if not self.cache:
            return None
            
        q_emb = self.embedder.embed_query(question)
        
        best_score = 0
        best_match = None
        
        for item in self.cache:
            score = self._cosine_similarity(q_emb, item["embedding"])
            if score > best_score:
                best_score = score
                best_match = item
                
        if best_score >= self.threshold and best_match:
            print(f"[CACHE HIT] Câu hỏi trùng khớp {best_score*100:.2f}% với câu cũ: '{best_match['question']}'")
            return best_match["answer_trace"]
            
        return None

    def add_to_cache(self, question: str, answer_trace: dict):
        q_emb = self.embedder.embed_query(question)
        self.cache.append({
            "question": question,
            "embedding": q_emb,
            "answer_trace": answer_trace
        })
        self._save_cache()

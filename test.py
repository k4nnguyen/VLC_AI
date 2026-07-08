import sys
sys.stdout.reconfigure(encoding='utf-8')

from db_init import init_database
from src.retrieval.retriever import Retriever
from src.retrieval.bm25_retriever import BM25Retriever
from src.retrieval.hybrid_rrf_retriever import HybridRRFRetriever

def build_database():
    return init_database()

store, chunks = build_database()

hybrid_retriever = HybridRRFRetriever(
    vector_retriever=Retriever(store),
    bm25_retriever=BM25Retriever(chunks),
    vector_k=5,
    bm25_k=5,
    final_k=5,
)

question = "Ngày lễ làm thêm giờ thì trả thêm ít nhất bao nhiêu tiền?"
print(f"Câu hỏi: {question}\n")

results = hybrid_retriever.retrieve(question, k=5)

for i, doc in enumerate(results["documents"][0]):
    meta = results["metadatas"][0][i]
    print(f"--- Top {i+1} | {meta['citation']} ---")
    print(doc)
    print("\n")
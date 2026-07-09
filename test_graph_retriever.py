import os
import json
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

from db_init import init_database
from src.retrieval.retriever import Retriever
from src.retrieval.bm25_retriever import BM25Retriever
from src.retrieval.hybrid_rrf_retriever import HybridRRFRetriever
from src.retrieval.graph_retriever import GraphRetriever

from src.loaders.docx_loader import DocxLoader
from src.cleaners.text_cleaner import TextCleaner
from src.parsing.structure_parser import StructureParser
from src.parsing.hierarchy_parser import HierarchyParser
from src.graph.graph_builder import KnowledgeGraphBuilder
from src.graph.concept_extractor import ConceptExtractor
from src.llm.openai_llm import OpenAILLM

def main():
    print("1. Đang khởi tạo Database và Embeddings...")
    store, chunks = init_database()
    
    print("2. Đang nạp Knowledge Graph từ cache...")
    llm = OpenAILLM(api_key=os.environ.get("OPENAI_API_KEY"))
    loader = DocxLoader()
    raw_doc = loader.load(Path("data/raw/lao_dong.docx"))
    legal_document = HierarchyParser().parse(StructureParser().parse(TextCleaner().clean(raw_doc)))
    
    extractor = ConceptExtractor(llm, cache_file="data/processed/concepts_cache.json")
    builder = KnowledgeGraphBuilder(concept_extractor=extractor)
    graph = builder.build(legal_document)

    print("3. Khởi tạo Retriever...")
    hybrid_retriever = HybridRRFRetriever(
        vector_retriever=Retriever(store),
        bm25_retriever=BM25Retriever(chunks),
        vector_k=3, # Chỉ lấy Top 3 cho dễ nhìn
        bm25_k=3,
        final_k=3,
    )
    
    graph_retriever = GraphRetriever(hybrid_retriever, graph)
    
    # ---------------------------------------------------------
    query = "Hợp đồng dưới 1 tháng có được giao kết bằng lời nói không?"
    print(f"\n========================================================")
    print(f"CÂU HỎI: {query}")
    print(f"========================================================\n")

    # TEST 1: Chỉ dùng Vector + BM25 (Không có Graph)
    print(">>> 1. KẾT QUẢ KHI KHÔNG CÓ ĐỒ THỊ (HYBRID RETRIEVER GỐC):")
    hybrid_results = hybrid_retriever.retrieve(query, k=3)
    for meta in hybrid_results["metadatas"][0]:
        print(f" - Tìm thấy: {meta.get('citation')}")
    
    # TEST 2: Có Graph Expansion
    print("\n>>> 2. KẾT QUẢ KHI CÓ ĐỒ THỊ (GRAPH RETRIEVER):")
    graph_results = graph_retriever.retrieve(query, k=3)
    
    original_docs = []
    expanded_refs = []
    expanded_ctx = []
    
    for meta in graph_results["metadatas"][0]:
        t = meta.get('type')
        c = meta.get('citation')
        if t == 'reference':
            expanded_refs.append(c)
        elif t == 'context':
            expanded_ctx.append(c)
        else:
            original_docs.append(c)

    print(f" [*] Entry Points (Giống gốc): {', '.join(original_docs)}")
    print(f" [+] Graph leo sang Tham chiếu chéo (REFERS_TO): {', '.join(expanded_refs)}")
    print(f" [+] Graph leo ngược lên Bối cảnh cha (HAS_CLAUSE): {', '.join(expanded_ctx)}")
    
    print("\n>>> 3. NỘI DUNG VĂN BẢN TRUY XUẤT ĐƯỢC MỞ RỘNG (VÍ DỤ 1 DOC):")
    # In thử 1 đoạn văn bản mở rộng
    for doc, meta in zip(graph_results["documents"][0], graph_results["metadatas"][0]):
        if meta.get('type') == 'reference':
            print("-" * 50)
            print(f"Metadata: {meta}")
            print(doc[:200] + "...\n")
            break

if __name__ == "__main__":
    main()

import sys
import os

# Thay đổi thư mục làm việc (Working Directory) về thư mục gốc của project
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)
os.chdir(PROJECT_ROOT)
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
from dotenv import load_dotenv

from db_init import init_database
from src.retrieval.retriever import Retriever
from src.retrieval.bm25_retriever import BM25Retriever
from src.retrieval.hybrid_rrf_retriever import HybridRRFRetriever
from src.llm.openai_llm import OpenAILLM
from src.rag.legal_rag import LegalRAG

load_dotenv()

app = FastAPI(title="VLC AI Backend API")

# Global RAG instance
rag_system = None
semantic_cache = None

@app.on_event("startup")
def startup_event():
    global rag_system, semantic_cache
    
    from src.rag.semantic_cache import SemanticCache
    semantic_cache = SemanticCache(threshold=0.95)
    
    print("Initializing Database and Models...")
    store, chunks = init_database()
    
    # Khởi tạo LLM trước
    llm = OpenAILLM(
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url=os.getenv("OPENAI_BASE_URL"),
        model=os.getenv("OPENAI_MODEL")
    )
    
    # Khởi tạo Knowledge Graph
    from pathlib import Path
    from src.loaders.docx_loader import DocxLoader
    from src.cleaners.text_cleaner import TextCleaner
    from src.parsing.structure_parser import StructureParser
    from src.parsing.hierarchy_parser import HierarchyParser
    from src.graph.graph_builder import KnowledgeGraphBuilder
    from src.graph.concept_extractor import ConceptExtractor
    from src.retrieval.graph_retriever import GraphRetriever

    print("Building Knowledge Graph from cache...")
    loader = DocxLoader()
    raw_doc = loader.load(Path("data/raw/lao_dong.docx"))
    legal_document = HierarchyParser().parse(StructureParser().parse(TextCleaner().clean(raw_doc)))
    
    # Tải cache concept lên đồ thị
    extractor = ConceptExtractor(llm, cache_file="data/processed/concepts_cache.json")
    builder = KnowledgeGraphBuilder(concept_extractor=extractor)
    graph = builder.build(legal_document)
    
    hybrid_retriever = HybridRRFRetriever(
        vector_retriever=Retriever(store),
        bm25_retriever=BM25Retriever(chunks),
        vector_k=15,
        bm25_k=15,
        final_k=15,
    )
    
    # Bọc Hybrid Retriever bằng Graph Retriever để mở rộng ngữ cảnh
    graph_retriever = GraphRetriever(hybrid_retriever, graph)
    
    rag_system = LegalRAG(graph_retriever, llm)
    
    # ---------------------------------------------------------
    # WARM-UP (LÀM NÓNG HỆ THỐNG): 
    # Chạy thử 1 câu hỏi ngầm để kích hoạt (load) các model Pytorch/BM25 
    # vào RAM và mở sẵn kết nối mạng (SSL handshake) với OpenAI. 
    # Việc này giúp câu hỏi ĐẦU TIÊN của user sau khi restart sẽ không bị chậm (Cold Start).
    print("Warming up models with a dummy query...")
    try:
        _ = rag_system.retrieve("warm up", k=1)
        # Nếu muốn warmup luôn cả OpenAI thì mở cmt dòng dưới (tốn 1 xíu API)
        # _ = rag_system.ask("warm up", k=1) 
    except Exception as e:
        print(f"Warmup warning: {e}")
        
    print("Graph RAG System Initialized and Ready!")

class QueryRequest(BaseModel):
    question: str
    k: int = 5

class Citation(BaseModel):
    article: int
    clause: int = None
    text: str = None

class QueryResponse(BaseModel):
    answer: str
    verified_citations: list[str]

@app.post("/ask", response_model=QueryResponse)
def ask_question(request: QueryRequest):
    if rag_system is None:
        raise HTTPException(status_code=503, detail="System is still initializing.")
    
    try:
        # TỐI ƯU 2: Kiểm tra Semantic Cache
        cached_trace = semantic_cache.get_cached_answer(request.question)
        if cached_trace:
            return QueryResponse(
                answer=cached_trace["answer"],
                verified_citations=cached_trace["verified_citations"]
            )

        # Nếu không có trong cache, chạy RAG bình thường
        trace = rag_system.ask_with_trace(request.question, k=request.k)
        
        # Lưu lại vào cache cho lần sau
        semantic_cache.add_to_cache(request.question, trace)

        return QueryResponse(
            answer=trace["answer"],
            verified_citations=trace["verified_citations"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

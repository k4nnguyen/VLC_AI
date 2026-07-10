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

# Global RAG instances
rag_systems = {}
semantic_caches = {}

@app.on_event("startup")
def startup_event():
    global rag_systems, semantic_caches
    
    from src.embeddings.embedding_model import EmbeddingModel
    from src.rag.semantic_cache import SemanticCache
    from pathlib import Path
    from src.loaders.docx_loader import DocxLoader
    from src.cleaners.text_cleaner import TextCleaner
    from src.parsing.structure_parser import StructureParser
    from src.parsing.hierarchy_parser import HierarchyParser
    from src.graph.graph_builder import KnowledgeGraphBuilder
    from src.graph.concept_extractor import ConceptExtractor
    from src.retrieval.graph_retriever import GraphRetriever

    print("Initializing Shared Models...")
    # Load EmbeddingModel ONE time to save RAM
    embedding_model = EmbeddingModel()
    
    llm = OpenAILLM(
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url=os.getenv("OPENAI_BASE_URL"),
        model=os.getenv("OPENAI_MODEL")
    )
    
    docs = ["lao_dong", "giao_thong"]
    for doc_name in docs:
        print(f"\n--- Initializing Domain: {doc_name.upper()} ---")
        
        # 1. Semantic Cache
        cache = SemanticCache(
            cache_file=f"data/processed/query_cache_{doc_name}.json", 
            threshold=0.95,
            embedder=embedding_model # Dùng chung mô hình để khỏi tốn RAM
        )
        semantic_caches[doc_name] = cache
        
        # 2. Database & Chunks
        store, chunks = init_database(doc_name=doc_name, embedding_model=embedding_model)
        
        # 3. Knowledge Graph
        print("Building Knowledge Graph from cache...")
        loader = DocxLoader()
        raw_doc = loader.load(Path(f"data/raw/{doc_name}.docx"))
        legal_document = HierarchyParser().parse(StructureParser().parse(TextCleaner().clean(raw_doc)))
        
        extractor = ConceptExtractor(llm, cache_file=f"data/processed/concepts_cache_{doc_name}.json")
        builder = KnowledgeGraphBuilder(concept_extractor=extractor)
        graph = builder.build(legal_document)
        
        # 4. Retrievers
        hybrid_retriever = HybridRRFRetriever(
            vector_retriever=Retriever(store),
            bm25_retriever=BM25Retriever(chunks),
            vector_k=15, bm25_k=15, final_k=15
        )
        
        graph_retriever = GraphRetriever(hybrid_retriever, graph)
        rag_sys = LegalRAG(graph_retriever, llm)
        
        # 5. Warm-up
        try:
            print("Warming up models with a dummy query...")
            _ = rag_sys.retrieve("warm up", k=1)
        except Exception as e:
            print(f"Warmup warning: {e}")
            
        rag_systems[doc_name] = rag_sys
        print(f"Graph RAG System for {doc_name} Initialized and Ready!")
        
    print("\n[+] All domains are ready to serve!")

class QueryRequest(BaseModel):
    question: str
    k: int = 5
    doc_name: str = "lao_dong"
    enable_reasoning: bool = True

class Citation(BaseModel):
    article: int
    clause: int = None
    text: str = None

class QueryResponse(BaseModel):
    answer: str
    verified_citations: list[str]

@app.post("/ask", response_model=QueryResponse)
def ask_question(request: QueryRequest):
    if not rag_systems:
        raise HTTPException(status_code=503, detail="System is still initializing.")
    
    doc_name = request.doc_name
    if doc_name not in rag_systems:
        raise HTTPException(status_code=404, detail=f"Domain '{doc_name}' not supported.")
        
    rag_system = rag_systems[doc_name]
    semantic_cache = semantic_caches[doc_name]
    
    try:
        # TỐI ƯU 2: Kiểm tra Semantic Cache
        cached_trace = semantic_cache.get_cached_answer(request.question, enable_reasoning=request.enable_reasoning)
        if cached_trace:
            return QueryResponse(
                answer=cached_trace["answer"],
                verified_citations=cached_trace["verified_citations"]
            )

        # Nếu không có trong cache, chạy RAG bình thường
        trace = rag_system.ask_with_trace(request.question, k=request.k, enable_reasoning=request.enable_reasoning)
        
        # Lưu lại vào cache cho lần sau
        semantic_cache.add_to_cache(request.question, trace, enable_reasoning=request.enable_reasoning)

        return QueryResponse(
            answer=trace["answer"],
            verified_citations=trace["verified_citations"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

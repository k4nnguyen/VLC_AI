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

@app.on_event("startup")
def startup_event():
    global rag_system
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
    print("Graph RAG System Initialized.")

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
        trace = rag_system.ask_with_trace(request.question, k=request.k)
        return QueryResponse(
            answer=trace["answer"],
            verified_citations=trace["verified_citations"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

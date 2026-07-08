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
    
    hybrid_retriever = HybridRRFRetriever(
        vector_retriever=Retriever(store),
        bm25_retriever=BM25Retriever(chunks),
        vector_k=15,
        bm25_k=15,
        final_k=15,
    )
    
    llm = OpenAILLM(
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url=os.getenv("OPENAI_BASE_URL"),
        model=os.getenv("OPENAI_MODEL")
    )
    
    rag_system = LegalRAG(hybrid_retriever, llm)
    print("RAG System Initialized.")

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

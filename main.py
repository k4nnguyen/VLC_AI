from pathlib import Path
import os
import sys
from dotenv import load_dotenv
from db_init import init_database
from src.retrieval.retriever import Retriever
from src.llm.openai_llm import OpenAILLM
from src.rag.legal_rag import LegalRAG
from src.evaluation.evaluator import RetrieverEvaluator
from src.retrieval.bm25_retriever import BM25Retriever
from src.retrieval.hybrid_rrf_retriever import HybridRRFRetriever
from src.evaluation.report_writer import ReportWriter

def build_database():
    return init_database()


def main():
    load_dotenv()
    store, chunks = build_database()
    hybrid_retriever = HybridRRFRetriever(
        vector_retriever=Retriever(store),
        bm25_retriever=BM25Retriever(chunks),
        vector_k=5,
        bm25_k=5,
        final_k=5,
    )
    llm = OpenAILLM(
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url=os.getenv("OPENAI_BASE_URL"),
        model=os.getenv("OPENAI_MODEL")
    )

    rag = LegalRAG(hybrid_retriever, llm)

    print("=" * 60)
    print("LEGAL RAG CHAT")
    print("Nhập câu hỏi, gõ 'exit' để thoát.")
    print("=" * 60)

    def print_trace(trace: dict):
        print("-" * 60)
        print("Retrieved context:")
        print(trace["context"])
        print("-" * 60)
        print("Verified citations:")
        for citation in trace["verified_citations"]:
            print(f"- {citation}")
        print("-" * 60)
        print("Assistant:")
        print(trace["answer"])
        print("-" * 60)

    if not sys.stdin.isatty():
        for raw_question in sys.stdin:
            question = raw_question.strip()
            if not question:
                continue
            if question.lower() in {"exit", "quit"}:
                break

            trace = rag.ask_with_trace(question, k=5)
            print_trace(trace)
        return

    while True:
        try:
            question = input("You: ").strip()
        except EOFError:
            break

        if not question:
            continue
        if question.lower() in {"exit", "quit"}:
            break

        trace = rag.ask_with_trace(question, k=5)
        print_trace(trace)

if __name__ == "__main__":
    main()
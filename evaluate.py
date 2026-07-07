from pathlib import Path
import os
from dotenv import load_dotenv
from src.loaders.docx_loader import DocxLoader
from src.cleaners.text_cleaner import TextCleaner
from src.parsing.structure_parser import StructureParser
from src.parsing.hierarchy_parser import HierarchyParser
from src.chunking.legal_chunker import LegalChunker
from src.embeddings.embedding_model import EmbeddingModel
from src.vectordb.chroma_store import ChromaStore
from src.retrieval.retriever import Retriever
from src.llm.openai_llm import OpenAILLM
from src.rag.legal_rag import LegalRAG
from src.evaluation.evaluator import RetrieverEvaluator
from src.retrieval.bm25_retriever import BM25Retriever
from src.evaluation.report_writer import ReportWriter

def build_database():
    loader = DocxLoader()
    raw_doc = loader.load(
        Path("data/raw/lao_dong.docx")
    )
    cleaner = TextCleaner()
    clean_doc = cleaner.clean(raw_doc)
    structure_parser = StructureParser()
    legal_doc = structure_parser.parse(clean_doc)
    hierarchy_parser = HierarchyParser()
    legal_doc = hierarchy_parser.parse(legal_doc)
    chunker = LegalChunker()
    chunks = chunker.chunk(legal_doc)
    embedding_model = EmbeddingModel()
    store = ChromaStore(embedding_model)
    store.reset()
    store.add(chunks)
    return store, chunks


def print_overall_report(method: str, report: dict):
    print("=" * 60)
    print(method.upper())
    print("=" * 60)

    for key, value in report["overall"].items():
        print(f"{key:<15}: {value}")


def main():
    load_dotenv()
    store, chunks = build_database()
    
    retriever = Retriever(store)
    evaluator = RetrieverEvaluator(retriever)
    report = evaluator.evaluate(k=5)
    print_overall_report("embedding", report)

    writer = ReportWriter()
    writer.save(
        report,
        method="embedding"
    )
    
    bm25 = BM25Retriever(chunks)
    evaluator = RetrieverEvaluator(bm25)
    report = evaluator.evaluate(k=5)
    print_overall_report("bm25", report)

    writer.save(
        report,
        method="bm25"
    )

if __name__ == "__main__":
    main()
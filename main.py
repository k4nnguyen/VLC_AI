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
from src.retrieval.hybrid_rrf_retriever import HybridRRFRetriever
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


def main():
    load_dotenv()
    store, chunks = build_database()
    # retriever = Retriever(store)
    # llm = OpenAILLM(
    #     api_key=os.getenv("OPENAI_API_KEY"),
    #     base_url=os.getenv("OPENAI_BASE_URL"),
    #     model=os.getenv("OPENAI_MODEL")
    # )
    
    # rag = LegalRAG(retriever,llm)
    # evaluator = RetrieverEvaluator(retriever)
    # report = evaluator.evaluate(k=5)
    # print("=" * 60)
    # print("Overall")
    # print("=" * 60)
    # print(f"Recall@5   : {report['Recall@K']:.3f}")
    # print(f"Precision  : {report['Precision@K']:.3f}")
    # print(f"MRR        : {report['MRR']:.3f}")
    # print(f"Hit Rate   : {report['HitRate']:.3f}")

    # print()

    # print("=" * 60)
    # print("Failed Cases")
    # print("=" * 60)

    # for item in report["details"]:

    #     if item["hit"]:
    #         continue

    #     print(item["question"])
    #     print("Expected :", item["expected"])
    #     print("Retrieved:", item["retrieved"])
    #     print("-" * 50)
    vector_retriever = Retriever(store)
    evaluator = RetrieverEvaluator(vector_retriever)
    report = evaluator.evaluate(k=5)
    writer = ReportWriter()

    writer.save(
        report,
        method="embedding"
    )
    
    bm25_retriever = BM25Retriever(chunks)
    evaluator = RetrieverEvaluator(bm25_retriever)
    report = evaluator.evaluate(k=5)
    writer.save(
        report,
        method="bm25"
    )

    hybrid_retriever = HybridRRFRetriever(
        vector_retriever=vector_retriever,
        bm25_retriever=bm25_retriever,
        vector_k=5,
        bm25_k=5,
        final_k=5,
    )
    evaluator = RetrieverEvaluator(hybrid_retriever)
    report = evaluator.evaluate(k=5)
    writer.save(
        report,
        method="hybrid_rrf"
    )

if __name__ == "__main__":
    main()
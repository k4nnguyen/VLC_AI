from dotenv import load_dotenv
import json
import os
from pathlib import Path

from db_init import init_database
from src.evaluation.generation_evaluator import GenerationEvaluator
from src.evaluation.report_writer import ReportWriter
from src.llm.openai_llm import OpenAILLM
from src.rag.legal_rag import LegalRAG
from src.retrieval.bm25_retriever import BM25Retriever
from src.retrieval.hybrid_rrf_retriever import HybridRRFRetriever
from src.retrieval.retriever import Retriever


def main():
    load_dotenv()
    store, chunks = init_database()

    dataset_path = Path("src/evaluation/generated_dataset.json")
    with open(dataset_path, "r", encoding="utf-8") as file:
        samples = json.load(file)

    if any("reference_answer" not in sample for sample in samples):
        raise ValueError(
            "generated_dataset.json is missing reference_answer fields. "
            "Run generate_evaluation.py again after updating the generator."
        )

    llm = OpenAILLM(
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url=os.getenv("OPENAI_BASE_URL"),
        model=os.getenv("OPENAI_MODEL"),
    )

    rag = LegalRAG(
        HybridRRFRetriever(
            vector_retriever=Retriever(store),
            bm25_retriever=BM25Retriever(chunks),
            vector_k=5,
            bm25_k=5,
            final_k=5,
        ),
        llm,
    )

    evaluator = GenerationEvaluator(rag)
    report = evaluator.evaluate(samples, k=5)

    writer = ReportWriter()
    writer.save_generation(report, method="generation")

    print("GENERATION EVALUATION")
    print(report["overall"])


if __name__ == "__main__":
    main()
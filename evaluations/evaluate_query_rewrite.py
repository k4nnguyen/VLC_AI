from dotenv import load_dotenv
import os

from db_init import init_database
from src.evaluation.query_rewrite_evaluator import QueryRewriteEvaluator
from src.evaluation.report_writer import ReportWriter
from src.llm.openai_llm import OpenAILLM
from src.rag.query_rewriter import QueryRewriter
from src.retrieval.bm25_retriever import BM25Retriever
from src.retrieval.hybrid_rrf_retriever import HybridRRFRetriever
from src.retrieval.retriever import Retriever


def main():
    load_dotenv()
    store, chunks = init_database()

    retriever = HybridRRFRetriever(
        vector_retriever=Retriever(store),
        bm25_retriever=BM25Retriever(chunks),
        vector_k=5,
        bm25_k=5,
        final_k=5,
    )

    llm = OpenAILLM(
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url=os.getenv("OPENAI_BASE_URL"),
        model=os.getenv("OPENAI_MODEL"),
    )

    evaluator = QueryRewriteEvaluator(retriever=retriever, query_rewriter=QueryRewriter(llm))
    report = evaluator.evaluate(k=5)

    writer = ReportWriter()
    writer.save(report["baseline"], method="query_rewrite_baseline")
    writer.save(report["rewritten"], method="query_rewrite_rewritten")

    comparison = {
        "summary": report["delta"],
        "groups": {
            "improved": [item for item in report["rewritten"]["details"] if not item["baseline_hit"] and item["hit"]],
            "regressed": [item for item in report["rewritten"]["details"] if item["baseline_hit"] and not item["hit"]],
            "unchanged": [item for item in report["rewritten"]["details"] if item["baseline_hit"] == item["hit"]],
        },
    }
    writer.save_comparison(comparison, method="query_rewrite_comparison")

    print("QUERY REWRITE EVALUATION")
    print("Baseline:", report["baseline"]["overall"])
    print("Rewritten:", report["rewritten"]["overall"])
    print("Delta:", report["delta"])


if __name__ == "__main__":
    main()
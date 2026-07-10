from pathlib import Path
import os
from dotenv import load_dotenv
from db_init import init_database
from src.retrieval.retriever import Retriever
from src.llm.openai_llm import OpenAILLM
from src.rag.legal_rag import LegalRAG
from src.evaluation.evaluator import RetrieverEvaluator
from src.retrieval.bm25_retriever import BM25Retriever
from src.retrieval.hybrid_rrf_retriever import HybridRRFRetriever
from src.evaluation.report_writer import ReportWriter

def build_database(doc_name: str):
    return init_database(doc_name=doc_name)


def print_overall_report(method: str, report: dict):
    print("=" * 60)
    print(method.upper())
    print("=" * 60)

    for key, value in report["overall"].items():
        print(f"{key:<15}: {value}")


def build_comparison(embedding_report: dict, bm25_report: dict):
    bm25_by_index = {
        item["index"]: item
        for item in bm25_report["details"]
    }

    groups = {
        "miss_both": [],
        "miss_embedding_only": [],
        "miss_bm25_only": [],
        "hit_both": []
    }

    for embedding_item in embedding_report["details"]:
        bm25_item = bm25_by_index.get(embedding_item["index"])
        if bm25_item is None:
            continue

        comparison_item = {
            "index": embedding_item["index"],
            "category": embedding_item.get("category", "unknown"),
            "question": embedding_item["question"],
            "expected": embedding_item["expected"],
            "embedding_hit": embedding_item["hit"],
            "bm25_hit": bm25_item["hit"]
        }

        if not embedding_item["hit"] and not bm25_item["hit"]:
            groups["miss_both"].append(comparison_item)
        elif not embedding_item["hit"] and bm25_item["hit"]:
            groups["miss_embedding_only"].append(comparison_item)
        elif embedding_item["hit"] and not bm25_item["hit"]:
            groups["miss_bm25_only"].append(comparison_item)
        else:
            groups["hit_both"].append(comparison_item)

    return {
        "summary": {
            "total": len(embedding_report["details"]),
            "miss_both": len(groups["miss_both"]),
            "miss_embedding_only": len(groups["miss_embedding_only"]),
            "miss_bm25_only": len(groups["miss_bm25_only"]),
            "hit_both": len(groups["hit_both"])
        },
        "groups": groups
    }


def print_comparison(comparison: dict):
    print("=" * 60)
    print("COMPARISON")
    print("=" * 60)
    for key, value in comparison["summary"].items():
        print(f"{key:<20}: {value}")

    for group_name, items in comparison["groups"].items():
        print()
        print(f"[{group_name}] {len(items)}")
        for item in items:
            print(f"- ({item['index']}) [{item['category']}] {item['question']}")


def main():
    load_dotenv()
    
    docs = ["lao_dong", "giao_thong"]
    vector_retrievers = {}
    bm25_retrievers = {}
    hybrid_retrievers = {}
    
    for doc_name in docs:
        print(f"Loading database for {doc_name}...")
        store, chunks = build_database(doc_name)
        
        vector_retriever = Retriever(store)
        bm25_retriever = BM25Retriever(chunks)
        hybrid_retriever = HybridRRFRetriever(
            vector_retriever=vector_retriever,
            bm25_retriever=bm25_retriever,
            vector_k=5,
            bm25_k=5,
            final_k=5,
        )
        
        vector_retrievers[doc_name] = vector_retriever
        bm25_retrievers[doc_name] = bm25_retriever
        hybrid_retrievers[doc_name] = hybrid_retriever

    print("Evaluating Vector Retriever...")
    evaluator = RetrieverEvaluator(vector_retrievers)
    embedding_report = evaluator.evaluate(k=5)
    print_overall_report("embedding", embedding_report)

    writer = ReportWriter()
    writer.save(
        embedding_report,
        method="embedding"
    )
    
    print("Evaluating BM25 Retriever...")
    evaluator = RetrieverEvaluator(bm25_retrievers)
    bm25_report = evaluator.evaluate(k=5)
    print_overall_report("bm25", bm25_report)

    writer.save(
        bm25_report,
        method="bm25"
    )

    print("Evaluating Hybrid RRF Retriever...")
    evaluator = RetrieverEvaluator(hybrid_retrievers)
    hybrid_report = evaluator.evaluate(k=5)
    print_overall_report("hybrid_rrf", hybrid_report)

    writer.save(
        hybrid_report,
        method="hybrid_rrf"
    )

    comparison = build_comparison(
        embedding_report=embedding_report,
        bm25_report=bm25_report
    )
    print_comparison(comparison)
    writer.save_comparison(comparison)

if __name__ == "__main__":
    main()
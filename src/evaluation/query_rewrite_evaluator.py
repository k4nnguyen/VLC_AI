from src.evaluation.dataset import EVAL_DATASET
from src.evaluation.evaluator import RetrieverEvaluator
from src.evaluation.metrics import RetrievalMetrics


class QueryRewriteEvaluator:
    def __init__(self, retriever, query_rewriter=None):
        self.retriever = retriever
        self.query_rewriter = query_rewriter

    def evaluate(self, k: int = 5):
        baseline_evaluator = RetrieverEvaluator(self.retriever)
        baseline_report = baseline_evaluator.evaluate(k=k)

        if self.query_rewriter is None:
            return {
                "baseline": baseline_report,
                "rewritten": None,
                "delta": None,
            }

        recalls = []
        precisions = []
        ranks = []
        hits = []
        details = []

        baseline_by_index = {
            item["index"]: item
            for item in baseline_report["details"]
        }

        for sample in EVAL_DATASET:
            sample_index = len(details)
            category = sample.get("category", "unknown")
            question = sample["question"]
            expected = baseline_evaluator._expected_articles(sample)
            rewritten_question = self.query_rewriter.rewrite(question)
            results = self.retriever.retrieve(rewritten_question, k=k)
            retrieved = [
                meta["article"]
                for meta in results["metadatas"][0]
            ]
            retrieved_set = set(retrieved)
            hit = len(expected & retrieved_set)
            recall = hit / len(expected) if expected else 0
            precision = hit / k
            recalls.append(recall)
            precisions.append(precision)
            hits.append(hit > 0)
            rank = 0
            for i, article in enumerate(retrieved, start=1):
                if article in expected:
                    rank = i
                    break

            ranks.append(rank)
            details.append({
                "index": sample_index,
                "category": category,
                "question": question,
                "rewritten_question": rewritten_question,
                "expected": list(expected),
                "retrieved": retrieved,
                "hit": hit > 0,
                "rank": rank,
                "recall": recall,
                "precision": precision,
                "baseline_hit": baseline_by_index[sample_index]["hit"],
                "baseline_rank": baseline_by_index[sample_index]["rank"],
            })

        rewritten_overall = {
            "questions": len(EVAL_DATASET),
            f"Recall@{k}": RetrievalMetrics.recall_at_k(recalls),
            f"Precision@{k}": RetrievalMetrics.precision_at_k(precisions),
            "MRR": RetrievalMetrics.mrr(ranks),
            "HitRate": RetrievalMetrics.hit_rate(hits),
            "Success": sum(hits),
            "Failed": len(hits) - sum(hits),
            "AvgRank": round(
                sum(rank for rank in ranks if rank > 0) / max(1, sum(hits)),
                3,
            ),
        }

        return {
            "baseline": baseline_report,
            "rewritten": {
                "overall": rewritten_overall,
                "details": details,
            },
            "delta": {
                "HitRate": rewritten_overall["HitRate"] - baseline_report["overall"]["HitRate"],
                "MRR": rewritten_overall["MRR"] - baseline_report["overall"]["MRR"],
                f"Recall@{k}": rewritten_overall[f"Recall@{k}"] - baseline_report["overall"][f"Recall@{k}"],
                f"Precision@{k}": rewritten_overall[f"Precision@{k}"] - baseline_report["overall"][f"Precision@{k}"],
            },
        }
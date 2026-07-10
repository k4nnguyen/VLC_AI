import json
from pathlib import Path
from src.evaluation.metrics import RetrievalMetrics

dataset_path = Path(__file__).parent / "generated_dataset.json"
with open(dataset_path, "r", encoding="utf-8") as f:
    EVAL_DATASET = json.load(f)
from src.evaluation.metrics import RetrievalMetrics

class RetrieverEvaluator:
    def __init__(self, retriever_dict):
        # retriever_dict is a dict mapping law (str) -> retriever instance
        self.retriever_dict = retriever_dict

    def _expected_articles(self, sample):
        if "expected" in sample:
            return {
                item["article"]
                for item in sample["expected"]
                if "article" in item
            }

        if "expected_articles" in sample:
            return set(sample["expected_articles"])

        return set()

    def evaluate(self, k=5):
        recalls = []
        precisions = []
        ranks = []
        hits = []
        details = []
        for sample in EVAL_DATASET:
            sample_index = len(details)
            category = sample.get("category", "unknown")
            question = sample["question"]
            law = sample.get("law", "lao_dong")
            expected = self._expected_articles(sample)
            
            retriever = self.retriever_dict[law]
            results = retriever.retrieve(question, k)
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
                "expected": list(expected),
                "retrieved": retrieved,
                "hit": hit > 0,
                "rank": rank,
                "recall": recall,
                "precision": precision
            })

        # ==========================
        # Overall metrics
        # ==========================

        overall = {
            "questions": len(EVAL_DATASET),
            "Recall@{}".format(k):
                RetrievalMetrics.recall_at_k(recalls),
            "Precision@{}".format(k):
                RetrievalMetrics.precision_at_k(precisions),
            "MRR":
                RetrievalMetrics.mrr(ranks),
            "HitRate":
                RetrievalMetrics.hit_rate(hits),
            "Success":
                sum(hits),
            "Failed":
                len(hits) - sum(hits),
            "AvgRank":
                round(
                    sum(r for r in ranks if r > 0) /
                    max(1, sum(hits)),
                    3
                )
        }
        return {
            "overall": overall,
            "details": details
        }
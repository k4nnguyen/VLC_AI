from src.evaluation.dataset import EVAL_DATASET
from src.evaluation.metrics import RetrievalMetrics

class RetrieverEvaluator:

    def __init__(self, retriever):
        self.retriever = retriever

    def evaluate(self, k=5):
        recalls = []
        precisions = []
        ranks = []
        hits = []
        details = []
        for sample in EVAL_DATASET:
            question = sample["question"]
            if "expected" in sample:
                expected = {x["article"] for x in sample["expected"]}
            else:
                expected = set(sample["expected_articles"])
            results = self.retriever.retrieve(question, k)
            retrieved = [
                meta["article"]
                for meta in results["metadatas"][0]
            ]
            retrieved_set = set(retrieved)
            hit = len(expected & retrieved_set)
            recall = hit / len(expected)
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
            details.append(
                {
                    "question": question,
                    "expected": list(expected),
                    "retrieved": retrieved,
                    "hit": hit > 0,
                    "rank": rank,
                    "recall": recall,
                    "precision": precision,
                }
            )

        return {
            "Recall@K": RetrievalMetrics.recall_at_k(recalls),
            "Precision@K": RetrievalMetrics.precision_at_k(precisions),
            "MRR": RetrievalMetrics.mrr(ranks),
            "HitRate": RetrievalMetrics.hit_rate(hits),
            "details": details,
        }
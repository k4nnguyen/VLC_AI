from src.evaluation.generation_metrics import GenerationMetrics


class GenerationEvaluator:
    def __init__(self, rag):
        self.rag = rag

    def evaluate(self, samples: list[dict], k: int = 5):
        references = []
        hypotheses = []
        contexts = []
        details = []

        for sample in samples:
            error = None
            try:
                trace = self.rag.ask_with_trace(sample["question"], k=k)
                answer = trace["answer"]
                context = trace["context"]
                verified_citations = trace.get("verified_citations", [])
            except Exception as exc:
                answer = ""
                context = ""
                verified_citations = []
                error = str(exc)

            references.append(sample.get("reference_answer", ""))
            hypotheses.append(answer)
            contexts.append(context)

            details.append({
                "question": sample["question"],
                "reference_answer": sample.get("reference_answer", ""),
                "answer": answer,
                "context": context,
                "verified_citations": verified_citations,
                "error": error,
            })

        bleu = GenerationMetrics.bleu(references, hypotheses)
        rouge = GenerationMetrics.rouge(references, hypotheses)
        faithfulness = GenerationMetrics.faithfulness(contexts, hypotheses)

        return {
            "overall": {
                "questions": len(samples),
                "BLEU": bleu,
                "ROUGE-1": rouge["rouge1"],
                "ROUGE-2": rouge["rouge2"],
                "ROUGE-L": rouge["rougeL"],
                "Faithfulness": faithfulness,
            },
            "details": details,
        }
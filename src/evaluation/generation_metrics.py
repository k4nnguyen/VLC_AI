from collections import Counter
from math import exp, log

from nltk.translate.bleu_score import SmoothingFunction, corpus_bleu
from rouge_score import rouge_scorer


class GenerationMetrics:
    @staticmethod
    def _tokenize(text: str) -> list[str]:
        return [token for token in text.lower().split() if token]

    @staticmethod
    def _char_ngrams(text: str, n: int) -> list[str]:
        compact = "".join(text.lower().split())
        if len(compact) < n:
            return []
        return [compact[index : index + n] for index in range(len(compact) - n + 1)]

    @classmethod
    def bleu(cls, references: list[str], hypotheses: list[str]) -> float:
        ref_tokens = [[cls._tokenize(reference)] for reference in references]
        hyp_tokens = [cls._tokenize(hypothesis) for hypothesis in hypotheses]
        return corpus_bleu(
            ref_tokens,
            hyp_tokens,
            smoothing_function=SmoothingFunction().method1,
        )

    @classmethod
    def rouge(cls, references: list[str], hypotheses: list[str]) -> dict:
        scorer = rouge_scorer.RougeScorer(["rouge1", "rouge2", "rougeL"], use_stemmer=False)
        totals = {"rouge1": 0.0, "rouge2": 0.0, "rougeL": 0.0}
        pairs = list(zip(references, hypotheses))

        if not pairs:
            return {key: 0.0 for key in totals}

        for reference, hypothesis in pairs:
            scores = scorer.score(reference, hypothesis)
            for key in totals:
                totals[key] += scores[key].fmeasure

        return {key: value / len(pairs) for key, value in totals.items()}

    @classmethod
    def faithfulness(cls, contexts: list[str], answers: list[str]) -> float:
        if not contexts or not answers:
            return 0.0

        matched = 0
        for context, answer in zip(contexts, answers):
            context_tokens = Counter(cls._tokenize(context))
            answer_tokens = cls._tokenize(answer)
            if not answer_tokens:
                continue
            overlap = sum(1 for token in answer_tokens if context_tokens[token] > 0)
            if overlap / max(1, len(answer_tokens)) >= 0.5:
                matched += 1

        return matched / len(list(zip(contexts, answers)))
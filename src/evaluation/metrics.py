class RetrievalMetrics:
    @staticmethod
    def hit_rate(hit_list):
        return sum(hit_list) / len(hit_list)

    @staticmethod
    def recall_at_k(recalls):
        return sum(recalls) / len(recalls)

    @staticmethod
    def precision_at_k(precisions):
        return sum(precisions) / len(precisions)

    @staticmethod
    def mrr(ranks):
        score = 0

        for rank in ranks:
            if rank == 0:
                continue
            score += 1 / rank

        return score / len(ranks)
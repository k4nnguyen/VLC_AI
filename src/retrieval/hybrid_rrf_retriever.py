class HybridRRFRetriever:
    def __init__(
        self,
        vector_retriever,
        bm25_retriever,
        vector_k: int = 5,
        bm25_k: int = 5,
        final_k: int = 5,
        rrf_k: int = 60,
    ):
        self.vector_retriever = vector_retriever
        self.bm25_retriever = bm25_retriever
        self.vector_k = vector_k
        self.bm25_k = bm25_k
        self.final_k = final_k
        self.rrf_k = rrf_k

    def _collect_ranked_items(self, results: dict):
        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        ids = results.get("ids", [[]])[0]

        ranked_items = []
        for rank, (document, metadata, chunk_id) in enumerate(
            zip(documents, metadatas, ids),
            start=1,
        ):
            article = metadata.get("article")
            if article is None:
                continue

            ranked_items.append({
                "rank": rank,
                "article": article,
                "document": document,
                "metadata": metadata,
                "id": chunk_id,
            })

        return ranked_items

    def retrieve(self, question: str, k: int = None):
        final_k = self.final_k if k is None else k

        vector_results = self.vector_retriever.retrieve(
            question,
            k=self.vector_k,
        )
        bm25_results = self.bm25_retriever.retrieve(
            question,
            k=self.bm25_k,
        )

        combined = {}

        def add_source(items, source_name):
            for item in items:
                chunk_id = item["id"]
                rrf_score = 1 / (self.rrf_k + item["rank"])

                if chunk_id not in combined:
                    combined[chunk_id] = {
                        "document": item["document"],
                        "metadata": dict(item["metadata"]),
                        "id": item["id"],
                        "score": 0.0,
                        "best_rank": item["rank"],
                        "vector_rank": None,
                        "bm25_rank": None,
                    }

                combined[chunk_id]["score"] += rrf_score
                combined[chunk_id]["best_rank"] = min(
                    combined[chunk_id]["best_rank"],
                    item["rank"],
                )
                combined[chunk_id][f"{source_name}_rank"] = item["rank"]

        add_source(self._collect_ranked_items(vector_results), "vector")
        add_source(self._collect_ranked_items(bm25_results), "bm25")

        # Apply custom scoring heuristics
        for item in combined.values():
            if item["vector_rank"] is not None and item["bm25_rank"] is not None:
                # Tăng 20% điểm nếu xuất hiện ở cả 2 bên (ưu tiên cao nhất)
                item["score"] *= 1.2
            elif item["vector_rank"] is not None and item["bm25_rank"] is None:
                # Tăng 10% điểm nếu chỉ xuất hiện ở Vector (ưu tiên Semantic Search hơn BM25)
                item["score"] *= 1.1

        reranked = sorted(
            combined.values(),
            key=lambda item: (-item["score"], item["best_rank"]),
        )[:final_k]

        return {
            "documents": [[item["document"] for item in reranked]],
            "metadatas": [[{
                **item["metadata"],
                "rrf_score": item["score"],
                "vector_rank": item["vector_rank"],
                "bm25_rank": item["bm25_rank"],
            } for item in reranked]],
            "ids": [[item["id"] for item in reranked]],
            "scores": [[item["score"] for item in reranked]],
        }
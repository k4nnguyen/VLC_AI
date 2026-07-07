class Retriever:
    def __init__(self, store):
        self.store = store

    def retrieve(
        self,
        question: str,
        k: int = 5
    ):
        results = self.store.search(
            query=question,
            k=k
        )
        documents = []
        metadatas = []
        distances = []
        ids = []
        seen_articles = set()
        for doc, meta, distance, chunk_id in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
            results["ids"][0]
        ):
            article = meta["article"]
            if article in seen_articles:
                continue
            seen_articles.add(article)
            documents.append(doc)
            metadatas.append(meta)
            distances.append(distance)
            ids.append(chunk_id)
            if len(documents) >= k:
                break
        return {
            "documents": [documents],
            "metadatas": [metadatas],
            "distances": [distances],
            "ids": [ids]
        }
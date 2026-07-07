import BM25


class BM25Retriever:
    def __init__(self, chunks):
        self.chunks = chunks
        corpus = [
            chunk.text
            for chunk in chunks
        ]
        # Build BM25 index
        self.retriever = BM25.index(corpus)

        # Map document -> Chunk
        self.chunk_map = {
            chunk.text: chunk
            for chunk in chunks
        }

    def retrieve(
        self,
        question: str,
        k: int = 5
    ):
        results = self.retriever.search(
            [question],
            k=k
        )[0]
        documents = []
        metadatas = []
        ids = []
        scores = []
        seen_articles = set()

        for result in results:
            document = result["document"]
            score = result["score"]
            chunk = self.chunk_map[document]
            article = chunk.metadata["article"]

            if article in seen_articles:
                continue
            seen_articles.add(article)
            documents.append(chunk.text)
            metadatas.append(chunk.metadata)
            ids.append(chunk.chunk_id)
            scores.append(score)
            if len(documents) == k:
                break
        return {
            "documents": [documents],
            "metadatas": [metadatas],
            "ids": [ids],
            "scores": [scores]
        }
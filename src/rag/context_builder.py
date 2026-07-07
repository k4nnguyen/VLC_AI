class ContextBuilder:
    def build(self, results) -> str:
        documents = results["documents"][0]
        metadatas = results["metadatas"][0]
        contexts = []
        
        for doc, meta in zip(documents, metadatas):
            contexts.append(f"""[{meta["citation"]}]  {doc} """)
        return "\n\n".join(contexts)
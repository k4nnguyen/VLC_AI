from src.rag.context_builder import ContextBuilder
from src.llm.prompt_builder import PromptBuilder
from src.verification.citation_verifier import CitationVerifier

class LegalRAG:
    def __init__(self, retriever, llm):
        self.retriever = retriever
        self.llm = llm 
        self.context_builder = ContextBuilder()
        self.prompt_builder = PromptBuilder()
        self.citation_verifier = CitationVerifier()

    def retrieve(self, question: str, k: int = 5):
        results = self.retriever.retrieve(question, k=k)
        return question, results

    def build_context(self, results) -> str:
        return self.context_builder.build(results)

    def build_messages(self, question: str, context: str) -> list[dict]:
        return self.prompt_builder.build(context=context, question=question)
        
    def ask(self, question: str, k: int = 5) -> str:
        _, results = self.retrieve(question, k=k)
        context = self.build_context(results)
        messages = self.build_messages(question=question, context=context)
        return self.llm.chat(messages)

    def ask_with_trace(self, question: str, k: int = 5) -> dict:
        rewritten_question, results = self.retrieve(question, k=k)
        context = self.build_context(results)
        messages = self.build_messages(question=question, context=context)
        answer = self.llm.chat(messages)

        allowed_citations = {
            meta.get("citation", "")
            for meta in results["metadatas"][0]
            if meta.get("citation")
        }
        verified_citations = self.citation_verifier.verify_answer(
            answer,
            allowed_citations,
        )

        return {
            "question": question,
            "rewritten_question": rewritten_question,
            "results": results,
            "context": context,
            "messages": messages,
            "answer": answer,
            "verified_citations": sorted(verified_citations),
        }
    
        

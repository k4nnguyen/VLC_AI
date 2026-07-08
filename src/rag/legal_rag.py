from src.rag.context_builder import ContextBuilder
from src.llm.prompt_builder import PromptBuilder
from src.verification.citation_verifier import CitationVerifier
from src.cleaners.query_preprocessor import QueryPreprocessor

class LegalRAG:
    def __init__(self, retriever, llm):
        self.retriever = retriever
        self.llm = llm 
        self.context_builder = ContextBuilder()
        self.prompt_builder = PromptBuilder()
        self.citation_verifier = CitationVerifier()
        self.query_preprocessor = QueryPreprocessor()

    def rewrite_query(self, question: str) -> str:
        from src.llm.prompt_builder import REWRITE_SYSTEM_PROMPT
        messages = [
            {"role": "system", "content": REWRITE_SYSTEM_PROMPT},
            {"role": "user", "content": question}
        ]
        try:
            # We use self.llm to generate the rewritten query
            rewritten = self.llm.chat(messages).strip()
            # Fallback to original question if LLM returns empty
            return rewritten if rewritten else question
        except Exception:
            return question

    def retrieve(self, question: str, k: int = 5):
        # 1. Ask LLM to rewrite query (add accents, fix slangs)
        rewritten_question = self.rewrite_query(question)
        
        # 2. Basic pre-processing (lowercase, spaces)
        clean_question = self.query_preprocessor.preprocess(rewritten_question)
        
        # 3. Retrieve
        results = self.retriever.retrieve(clean_question, k=k)
        return clean_question, results

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

        citation_to_content = {}
        for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
            citation = meta.get("citation")
            if citation:
                citation_to_content[citation] = doc

        detailed_citations = []
        for cite in sorted(verified_citations):
            content = citation_to_content.get(cite, "")
            detailed_citations.append(f"**{cite}**:\n\n{content.strip()}")

        return {
            "question": question,
            "rewritten_question": rewritten_question,
            "results": results,
            "context": context,
            "messages": messages,
            "answer": answer,
            "verified_citations": detailed_citations,
        }
    
        

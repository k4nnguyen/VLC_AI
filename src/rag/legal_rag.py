from src.rag.context_builder import ContextBuilder
from src.llm.prompt_builder import PromptBuilder

class LegalRAG:
    def __init__(self, retriever, llm):
        self.retriever = retriever
        self.llm = llm 
        self.context_builder = ContextBuilder()
        self.prompt_builder = PromptBuilder()
        
    def ask(self, question: str, k: int = 5) -> str:
        results = self.retriever.retrieve(question, k=k)
        context = self.context_builder.build(results)
        messages = self.prompt_builder.build(context=context,question=question)
        return self.llm.chat(messages)
    
        

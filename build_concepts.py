import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

from src.loaders.docx_loader import DocxLoader
from src.cleaners.text_cleaner import TextCleaner
from src.parsing.structure_parser import StructureParser
from src.parsing.hierarchy_parser import HierarchyParser
from src.llm.openai_llm import OpenAILLM
from src.graph.concept_extractor import ConceptExtractor
from src.graph.graph_builder import KnowledgeGraphBuilder

def main():
    print("1. Đang tải và phân tích văn bản luật...")
    loader = DocxLoader()
    raw_doc = loader.load(Path("data/raw/lao_dong.docx"))
    legal_document = HierarchyParser().parse(StructureParser().parse(TextCleaner().clean(raw_doc)))

    print("2. Khởi tạo OpenAI LLM và Concept Extractor...")
    llm = OpenAILLM(api_key=os.environ.get("OPENAI_API_KEY"))
    extractor = ConceptExtractor(llm, cache_file="data/processed/concepts_cache.json")

    print("3. Khởi chạy Knowledge Graph Builder (Có tích hợp Extract Concept)")
    builder = KnowledgeGraphBuilder(concept_extractor=extractor)
    for chapter in legal_document.chapters:
        # Quét các Điều nằm thẳng trong Chương
        for article in chapter.articles:
            print(f"-> Đang xử lý Điều {article.number}...")
            builder._add_article(article)
            
        # Quét các Điều nằm trong các Mục (Sections)
        for section in chapter.sections:
            for article in section.articles:
                print(f"-> Đang xử lý Điều {article.number} (Mục {section.number})...")
                builder._add_article(article)
            
    print("\n[+] Đã hoàn thành trích xuất! Các Concept đã được lưu vĩnh viễn vào 'data/processed/concepts_cache.json'")

if __name__ == "__main__":
    main()

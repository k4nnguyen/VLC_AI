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

import sys

def main():
    doc_name = "lao_dong"
    if len(sys.argv) > 1:
        doc_name = sys.argv[1]
        
    print(f"1. Đang tải và phân tích văn bản luật ({doc_name}.docx)...")
    loader = DocxLoader()
    raw_doc = loader.load(Path(f"data/raw/{doc_name}.docx"))
    legal_document = HierarchyParser().parse(StructureParser().parse(TextCleaner().clean(raw_doc)))

    print("2. Khởi tạo OpenAI LLM và Concept Extractor...")
    llm = OpenAILLM(api_key=os.environ.get("OPENAI_API_KEY"))
    extractor = ConceptExtractor(llm, cache_file=f"data/processed/concepts_cache_{doc_name}.json")

    print(f"3. Khởi chạy Knowledge Graph Builder cho {doc_name}...")
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
            
    print(f"\n[+] Đã hoàn thành trích xuất! Các Concept đã được lưu vào 'data/processed/concepts_cache_{doc_name}.json'")

if __name__ == "__main__":
    main()

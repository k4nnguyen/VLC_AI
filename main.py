from pathlib import Path
from src.loaders.docx_loader import DocxLoader
from src.cleaners.text_cleaner import TextCleaner
from src.parsing.structure_parser import StructureParser
from src.parsing.hierarchy_parser import HierarchyParser
from src.chunking.legal_chunker import LegalChunker
from src.embeddings.embedding_model import EmbeddingModel
from src.vectordb.chroma_store import ChromaStore
def main():
    # Load
    loader = DocxLoader()
    raw_doc = loader.load(Path("data/raw/lao_dong.docx"))

    # Clean
    cleaner = TextCleaner()
    clean_doc = cleaner.clean(raw_doc)

    # Parse structure
    structure_parser = StructureParser()
    legal_doc = structure_parser.parse(clean_doc)

    # Parse hierarchy
    hierarchy_parser = HierarchyParser()
    legal_doc = hierarchy_parser.parse(legal_doc)

    # Chunk
    chunker = LegalChunker()
    chunks = chunker.chunk(legal_doc)

    print("=" * 80)
    print(f"Total chunks: {len(chunks)}")
    print("=" * 80)

    # In thử 5 chunk đầu
    for chunk in chunks[:5]:
        print(chunk.model_dump())
        print("-" * 80)

    print(f"Total Chapters : {len(legal_doc.chapters)}")
    print(f"Total Chunks   : {len(chunks)}")
    print()
    first_chunk = chunks[0]
    print(first_chunk.chunk_id)
    print(first_chunk.metadata)
    print(first_chunk.text)
    
    embedding_model = EmbeddingModel()
    store = ChromaStore(embedding_model)
    store.reset()
    store.add(chunks)
    results = store.search(
    "Người lao động được nghỉ phép bao nhiêu ngày?",
    k=5
    )
    print(results)
    
if __name__ == "__main__":
    main()
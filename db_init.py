from pathlib import Path

from src.chunking.legal_chunker import LegalChunker
from src.cleaners.text_cleaner import TextCleaner
from src.embeddings.embedding_model import EmbeddingModel
from src.loaders.docx_loader import DocxLoader
from src.parsing.hierarchy_parser import HierarchyParser
from src.parsing.structure_parser import StructureParser
from src.vectordb.chroma_store import ChromaStore


def build_chunks():
	loader = DocxLoader()
	raw_doc = loader.load(Path("data/raw/lao_dong.docx"))
	cleaner = TextCleaner()
	clean_doc = cleaner.clean(raw_doc)
	structure_parser = StructureParser()
	legal_doc = structure_parser.parse(clean_doc)
	hierarchy_parser = HierarchyParser()
	legal_doc = hierarchy_parser.parse(legal_doc)
	chunker = LegalChunker()
	return chunker.chunk(legal_doc)


def init_chromadb(chunks=None):
	if chunks is None:
		chunks = build_chunks()

	embedding_model = EmbeddingModel()
	store = ChromaStore(embedding_model)

	if store.collection.count() == 0:
		store.add(chunks)

	return store, chunks


def init_database():
	return init_chromadb()


if __name__ == "__main__":
	store, chunks = init_database()
	try:
		count = store.collection.count()
	except Exception:
		count = "unknown"
	print(f"ChromaDB initialized or reused. Collection count: {count}")

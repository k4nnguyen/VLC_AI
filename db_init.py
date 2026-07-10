from pathlib import Path

from src.chunking.legal_chunker import LegalChunker
from src.cleaners.text_cleaner import TextCleaner
from src.embeddings.embedding_model import EmbeddingModel
from src.loaders.docx_loader import DocxLoader
from src.parsing.hierarchy_parser import HierarchyParser
from src.parsing.structure_parser import StructureParser
from src.vectordb.chroma_store import ChromaStore


def build_chunks(doc_name: str = "lao_dong"):
	loader = DocxLoader()
	raw_doc = loader.load(Path(f"data/raw/{doc_name}.docx"))
	cleaner = TextCleaner()
	clean_doc = cleaner.clean(raw_doc)
	structure_parser = StructureParser()
	legal_doc = structure_parser.parse(clean_doc)
	hierarchy_parser = HierarchyParser()
	legal_doc = hierarchy_parser.parse(legal_doc)
	chunker = LegalChunker()
	return chunker.chunk(legal_doc)


def init_chromadb(doc_name: str = "lao_dong", chunks=None, embedding_model=None):
	if chunks is None:
		chunks = build_chunks(doc_name)

	if embedding_model is None:
		embedding_model = EmbeddingModel()
		
	store = ChromaStore(embedding_model, collection_name=doc_name)

	if store.collection.count() == 0:
		store.add(chunks)

	return store, chunks


def init_database(doc_name: str = "lao_dong", embedding_model=None):
	return init_chromadb(doc_name=doc_name, embedding_model=embedding_model)


if __name__ == "__main__":
	store, chunks = init_database()
	try:
		count = store.collection.count()
	except Exception:
		count = "unknown"
	print(f"ChromaDB initialized or reused. Collection count: {count}")

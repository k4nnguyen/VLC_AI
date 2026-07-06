from pathlib import Path
from src.loaders.docx_loader import DocxLoader
from src.cleaners.text_cleaner import TextCleaner
from src.parsing.structure_parser import StructureParser

loader = DocxLoader()
cleaner = TextCleaner()
parser = StructureParser()

raw_doc = loader.load(Path("data/raw/lao_dong.docx"))
clean_doc = cleaner.clean(raw_doc)
legal_doc = parser.parse(clean_doc)

print(legal_doc.chapters[0])
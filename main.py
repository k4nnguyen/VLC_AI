from pathlib import Path
from src.cleaners.text_cleaner import TextCleaner
from src.loaders.docx_loader import DocxLoader

loader = DocxLoader()
document = loader.load(
    Path("data/raw/lao_dong.docx")
)
cleaner = TextCleaner()
cleaned = cleaner.clean(document)

print(cleaned.cleaned_text[:100])
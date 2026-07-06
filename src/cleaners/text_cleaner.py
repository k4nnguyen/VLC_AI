import re
from src.cleaners.base_cleaner import BaseCleaner
from src.core.models.raw_document import RawDocument
from src.core.models.cleaned_document import CleanedDocument

class TextCleaner(BaseCleaner):
    def clean(self, document: RawDocument) -> CleanedDocument:
        text = document.raw_text
        text = re.sub(r"\n{2,}", "\n", text) # Regex ký tự xuống dòng khi nhiều hơn 2 lần
        text = re.sub(r"[ \t]+", " ", text) # Regex ký tự tab
        text = text.strip()
        
        return CleanedDocument(
            raw_document=document,
            cleaned_text=text
        )